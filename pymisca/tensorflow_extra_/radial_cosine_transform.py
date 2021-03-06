# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.framework import ops
from tensorflow.python.framework import tensor_util
from tensorflow.python.ops import check_ops
from tensorflow.python.ops import control_flow_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops.distributions import bijector


from tensorflow.python.ops import nn
from tensorflow_probability.python import bijectors
from tensorflow_probability.python.distributions import TransformedDistribution,Normal

#### allow "simple = True" overider
from pymisca.tensorflow_extra_.tfp_transformed_distribution import TransformedDistribution

__all__ = [
    "RadialCosineTransform",
    "AsRadialCosine",
]


class RadialCosineTransform(bijector.Bijector):
  """
  """

  def __init__(self,
               D = 2,
               power=0.,
               event_ndims=1,
               validate_args=False,
               debug = False,
               name="radial_cosine_transform"):
    """Instantiates the `PowerTransform` bijector.

    Args:
      power: Python `float` scalar indicating the transform power, i.e.,
        `Y = g(X) = (1 + X * c)**(1 / c)` where `c` is the `power`.
      event_ndims: Python scalar indicating the number of dimensions associated
        with a particular draw from the distribution.
      validate_args: Python `bool` indicating whether arguments should be
        checked for correctness.
      name: Python `str` name given to ops managed by this object.

    Raises:
      ValueError: if `power < 0` or is not known statically.
    """
    self._graph_parents = []
    self._name = name
    self._validate_args = validate_args
#     self._D = tf.constant(D,dtype='int32')
    self.debug = debug
    with self._name_scope("init", values=[D]):
      D = tensor_util.constant_value(
          ops.convert_to_tensor(D, name="dimension")
      )
      self._D = D
      self.alpha = self._alpha = self._D / array_ops.constant(2.)
#     if power is None or power < 0:
#       raise ValueError("`power` must be a non-negative TF constant.")
#     self._power = power
    
    super(RadialCosineTransform, self).__init__(
        forward_min_event_ndims = 1,
        inverse_min_event_ndims = 1,        
#         event_ndims=event_ndims,
        validate_args=validate_args,
        name=name)


  @property
  def D(self):
    """D as in (D-1)-sphere S^{D-1}"""
    return self._D

  def _forward(self, x):
    raise Exception ("Not implemented yet")
    x = self._maybe_assert_valid_x(x)
    normal = Normal(loc=0.,scale=1.,)

    sp = array_ops.shape(x) ### use dynamical shape
    #### thanks to https://pgaleone.eu/tensorflow/2018/07/28/understanding-tensorflow-tensors-shape-static-dynamic/
    
    if self.debug:
        print (type(x),x)
        print ('xshape',x.shape)
    
    y = normal.sample( sp,)
    y = nn.l2_normalize(y,dim=-1) 
    
    if self.debug:
        print ('forward_sp',sp)
    if self.debug:
        print ('forward_xy',x.shape,y.shape)
        
        
    y = y *  math_ops.sqrt(x)
    return y


  def _inverse(self, y):
    y = self._maybe_assert_valid_y(y)
    rsq = math_ops.reduce_sum( math_ops.square(y),
                              axis = -1,
                              keepdims = True)
    y0 = array_ops.gather(y,[0],axis=-1,)
#     y0    =   array_ops.transpose( array_ops.transpose(y)[0:1],)    
    cosine = y0/math_ops.sqrt(rsq)

    x = array_ops.concat( [rsq, cosine], -1 )
    return x


  def _inverse_log_det_jacobian(self, y):
    y = self._maybe_assert_valid_y(y)
    x = self.inverse(y)
    val =  -self._forward_log_det_jacobian(x)
    return val

  def _forward_log_det_jacobian(self, x):
    x = self._maybe_assert_valid_x(x)
    
    rsq = array_ops.transpose(array_ops.transpose(x)[0])
    
    logDet = ( self.alpha -1 ) * math_ops.log(rsq) - math_ops.log(2.)
    
    return logDet


#     return math_ops.reduce_sum(x,)
#     if self.power == 0.:
#       return math_ops.reduce_sum(x, axis=event_dims)
#     return (1. / self.power - 1.) * math_ops.reduce_sum(
#         math_ops.log1p(x * self.power),
#         axis=event_dims)

  def _maybe_assert_valid_x(self, x):
    if not self.validate_args or self.power == 0.:
      return x
    is_valid = check_ops.assert_non_negative(
        1. + self.power * x,
        message="Forward transformation input must be at least {}.".format(
            -1. / self.power))
    return control_flow_ops.with_dependencies([is_valid], x)

  def _maybe_assert_valid_y(self, y):
    if not self.validate_args:
      return y
    is_valid = check_ops.assert_positive(
        y, message="Inverse transformation input must be greater than 0.")
    return control_flow_ops.with_dependencies([is_valid], y)

class AsRadialCosine(TransformedDistribution):
    ''' Transform a distribution on R^+ to distribution on R^D 
'''
    def __init__(self, distribution=None,D=None,debug=False,name='AsRadial'):
#         udist = tf.contrib.distributions.Uniform(low=0.,high=3.) 
        
        bjt = RadialCosineTransform(D = D,debug=debug,)
        super(AsRadialCosine,self).__init__(bijector=bjt,
                                         distribution=distribution,
                                         event_shape = [D],
                                         simple=1,
                                         name = name,
                                        )
    @property    
    def D(self,):
        return self.bijector.D
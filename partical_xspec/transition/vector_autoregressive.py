"""Transition function module.
"""
from tensorflow_probability import distributions as tfd
import tensorflow as tf

from partical_xspec.transition import util as trans_util
from partical_xspec.transition.transition import Transition


class TransitionVectorAutoregressive(Transition):
    """
    """
    def __init__(self, coefficients, noise_covariance, dtype=tf.float32):
        """
        """
        coefficients = tf.convert_to_tensor(coefficients, dtype=dtype)
        self.coefficients = coefficients
        self.order = coefficients.shape[-3]
        self.latent_size = coefficients.shape[-2]

        self.transition_matrix = trans_util.make_companion_matrix(
            coefficients)

        self.transition_noise_cov_chol = tf.linalg.LinearOperatorBlockDiag(
            [tf.linalg.LinearOperatorFullMatrix(
                tf.linalg.cholesky(noise_covariance)),
             tf.linalg.LinearOperatorIdentity(
                (self.order-1)*self.latent_size)]).to_dense()

        self.dtype = dtype

    def _transition_function(self):

        transition_matrix = self.transition_matrix
        transition_noise_cov_chol = self.transition_noise_cov_chol

        transition_matrix_transpose = tf.linalg.matrix_transpose(
            transition_matrix)

        def _transition_fn(_, x):
            x = tf.convert_to_tensor(x[tf.newaxis, :], self.dtype)
            fx = x @ transition_matrix_transpose
            transition_dist = tfd.MultivariateNormalTriL(
                loc=tf.squeeze(fx, axis=0),
                scale_tril=transition_noise_cov_chol)
            return transition_dist

        return _transition_fn

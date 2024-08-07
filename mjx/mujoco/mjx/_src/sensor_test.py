# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for sensor functions."""

from absl.testing import absltest
from absl.testing import parameterized
import jax
import mujoco
from mujoco import mjx
from mujoco.mjx._src import test_util
import numpy as np

# tolerance for difference between MuJoCo and MJX smooth calculations - mostly
# due to float precision
_TOLERANCE = 5e-5


def _assert_eq(a, b, name):
  tol = _TOLERANCE * 10  # avoid test noise
  err_msg = f'mismatch: {name}'
  np.testing.assert_allclose(a, b, err_msg=err_msg, atol=tol, rtol=tol)


def _assert_attr_eq(a, b, attr):
  _assert_eq(getattr(a, attr), getattr(b, attr), attr)


class SensorTest(parameterized.TestCase):

  @parameterized.parameters('no_sensor.xml', 'sensor.xml')
  def test_sensor(self, filename):
    """Tests MJX sensor functions match MuJoCo sensor functions."""
    m = test_util.load_test_file(filename)
    d = mujoco.MjData(m)
    # give the system a little kick to ensure we have non-identity rotations
    d.qvel = np.random.random(m.nv)
    # apply control for activation dynamics
    d.ctrl = np.clip(
        np.random.random(m.nu),
        m.actuator_ctrlrange[:, 0],
        m.actuator_ctrlrange[:, 1],
    )
    mujoco.mj_step(m, d, 10)  # let dynamics get state significantly non-zero
    mx = mjx.put_model(m)
    dx = mjx.put_data(m, d)

    mujoco.mj_forward(m, d)
    dx = jax.jit(mjx.forward)(mx, dx)

    # sensor values
    _assert_eq(d.sensordata, dx.sensordata, 'sensordata')


if __name__ == '__main__':
  absltest.main()

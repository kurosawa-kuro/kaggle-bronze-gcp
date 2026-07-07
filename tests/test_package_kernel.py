import unittest

from runner.ops.package_kernel import INFERENCE_SCRIPT


class PackageKernelTest(unittest.TestCase):
    def test_generated_inference_script_compiles(self):
        compile(INFERENCE_SCRIPT, "generated_inference.py", "exec")
        self.assertIn("import hashlib", INFERENCE_SCRIPT)


if __name__ == "__main__":
    unittest.main()

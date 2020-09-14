from jupyter_client.kernelspec import KernelSpecManager


class SysInsertManager(KernelSpecManager):
    def get_kernel_spec(self, kernel_name):
        init_resp = super().get_kernel_spec(kernel_name)
        init_resp.argv = [
            *init_resp.argv,
            "--IPKernelApp.exec_lines=['import sys', "
            """'sys.path.append("..")']""",
        ]
        return init_resp

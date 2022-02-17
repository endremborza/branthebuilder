from jupyter_client.kernelspec import KernelSpecManager


class SysInsertManager(KernelSpecManager):
    def get_kernel_spec(self, kernel_name):
        init_resp = super().get_kernel_spec(kernel_name)
        lines = ["import sys", 'sys.path.insert(0, "..")']
        line_str = ", ".join([f"'{s}'" for s in lines])
        init_resp.argv = [
            *init_resp.argv,
            f"--IPKernelApp.exec_lines=[{line_str}]",
        ]
        return init_resp

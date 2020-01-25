from jupyter_client.kernelspec import KernelSpecManager
from notebook.notebookapp import main


class MyManager(KernelSpecManager):
    def get_kernel_spec(self, kernel_name):
        init_resp = super().get_kernel_spec(kernel_name)
        init_resp.argv = [
            *init_resp.argv,
            """--IPKernelApp.exec_lines=['import sys', 'sys.path.append("..")']""",
        ]
        return init_resp


if __name__ == "__main__":
    main(kernel_spec_manager_class=MyManager)

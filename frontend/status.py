import psutil
from view_model import MenuPage, LineItem


class RootPage(MenuPage):
    def __init__(self, previous_page):
        super().__init__("Status", previous_page, has_sub_page=True, datastore=None)

    def page_content(self, index):
        if index == 0:
            disk = psutil.disk_usage('/')
            return LineItem('Disk Usage: ' + str(disk.percent) + "%")
        elif index == 1:
            disk = psutil.disk_usage('/')
            return LineItem('Disk Free: ' + str(disk.free // 1024 // 1024) + "MiB")
        elif index == 2:
            ram = psutil.virtual_memory()
            return LineItem('Mem Free: ' + str(ram.percent) + "%")
        elif index == 3:
            cpu = psutil.getloadavg()
            return LineItem('CPU Avg: ' + str(cpu))
        elif index == 4:
            cpu = psutil.cpu_freq()
            return LineItem('CPU Frq: ' + str(cpu.current) + "MHz")

    def total_size(self):
        return 5

    # TODO: Find out how to periodically update this page.

import asyncio
import xml.etree.ElementTree as ET
import pytak

from configparser import ConfigParser


def gen_cot():
    """Generate CoT Event."""
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", "a-h-A-M-A")
    root.set("uid", "name_your_marker")
    root.set("how", "m-g")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set(
        "stale", pytak.cot_time(60)
    )

    pt_attr = {
        "lat": "1.268",
        "lon": "103.82",
        "hae": "0",
        "ce": "10",
        "le": "10",
    }

    ET.SubElement(root, "point", attrib=pt_attr)

    return ET.tostring(root)


class MySender(pytak.QueueWorker):
    """
    Process or generate your Cursor-On-Target Events,
    then adds the COT Events to a queue for TX to a COT_URL.
    """

    async def handle_data(self, data):
        """Handle pre-CoT data, serialize to CoT Event, puts on queue."""
        event = data
        await self.put_queue(event)

    async def run(self):
        """Run loop for processing or generating pre-CoT data."""
        while True:
            data = gen_cot()
            self._logger.info("Sending:\n%s\n", data.decode())
            await self.handle_data(data)
            await asyncio.sleep(5)


class MyReceiver(pytak.QueueWorker):
    """Handle events from RX Queue."""

    async def handle_data(self, data):
        """Handle data from the receive queue."""
        self._logger.info("Received:\n%s\n", data.decode())

    async def run(self):
        """Read from the receive queue, put data onto handler."""
        while True:
            data = (
                await self.queue.get()
            )
            await self.handle_data(data)


async def main():
    """
    Sets config params and adds serializer to asyncio task list
    """
    config = ConfigParser()
    config["mycottool"] = {"COT_URL": "tcp://192.168.1.17:8087"}
    config = config["mycottool"]

    clitool = pytak.CLITool(config)
    await clitool.setup()

    clitool.add_tasks(
        [MySender(clitool.tx_queue, config)]
        # set([MySender(clitool.tx_queue, config), MyReceiver(clitool.rx_queue, config)])
    )
    await clitool.run()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor


async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='74iel8qv0gczba8y6ce3v7rpt1i704zf',
      api_key_id='abfa28b9-8013-4f96-be41-8dce890e73d9'
    )
    return await RobotClient.at_address('test-bench-main.jrh0bbfyer.viam.cloud', opts)

async def setup():
    robot = await connect()
    return robot

robot = asyncio.run(setup())

print('Resources:')
print(robot.resource_names)

phidgets = Sensor.from_robot(robot, "phidgets")
tare = {
    "command": "tare"
}

asyncio.run(phidgets.do_command(tare))

async def tare():
    await phidgets.do_command({'command': 'tare'})
    return 'tared'

async def weigh():
    weight = await phidgets.get_readings
    return weight

async def live_weigh():
    weight = await phidgets.do_command({'command': 'live_weigh'})
    return weight

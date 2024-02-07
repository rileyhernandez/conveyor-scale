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

async def main():
    robot = await connect()

    print('Resources:')
    print(robot.resource_names)
    
    # phidgets
    phidgets = Sensor.from_robot(robot, "phidgets")
    tare = {
        "command": "tare"
    }
    calibrate = {
        'command': 'calibrate'
    }
    await phidgets.do_command(calibrate)
 
    try:
        input('Press Enter to weigh...')
    except(Exception, KeyboardInterrupt):
        pass
    phidgets_return_value = await phidgets.get_readings()
    print(f"phidgets get_readings return value: {phidgets_return_value}")

    # Don't forget to close the machine when you're done!
    # await robot.close()

if __name__ == '__main__':
    asyncio.run(main())

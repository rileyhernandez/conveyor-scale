import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.motor import Motor


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
    phidgets_return_value = await phidgets.get_readings()
    print(f"phidgets get_readings return value: {phidgets_return_value}")
  
    # STF06-IP
    stf_06_ip = Motor.from_robot(robot, "STF06-IP")
    stf_06_ip_return_value = await stf_06_ip.is_moving()
    print(f"STF06-IP is_moving return value: {stf_06_ip_return_value}")

    # Don't forget to close the machine when you're done!
    await robot.close()

async def dispense(serving, rpm=100, step=1000, offset=5, n=10, inc_step=0.25):
    """Function that takes in a serving amount (and other settings) and dispenses that weight
    """
    robot = await connect()
    print('Resources:')
    print(robot.resource_names)
    scale = Sensor.from_robot(robot, "phidgets")
    motor = Motor.from_robot(robot, "STF06-IP")
    
    await motor.go_for(rpm, 500)
    msg = await scale.do_command({
                                    'command': 'weigh-until',
                                    'serving': serving,
                                    })
    await motor.stop()

    print(msg)
    await robot.close()

async def weigh():
    robot = await connect()
    scale = Sensor.from_robot(robot, 'phidgets')
    weight = await scale.get_readings()
    print('weight: ', weight['weight'])
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
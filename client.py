import asyncio
import matplotlib.pyplot as plt

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.motor import Motor


# async def connect():
#     opts = RobotClient.Options.with_api_key(
#       api_key='74iel8qv0gczba8y6ce3v7rpt1i704zf',
#       api_key_id='abfa28b9-8013-4f96-be41-8dce890e73d9'
#     )
#     return await RobotClient.at_address('test-bench-main.jrh0bbfyer.viam.cloud', opts)

class Data:

    def __init__(self):
        self.times = []
        self.weights = []
        self.avgs = []

    def log_weight(self, weight):
        if type(weight) != list:
            weight = [weight]
        self.weights += weight

    def log_avg(self, avg):
        self.avgs += [avg]
    
    def plot_weight_data(self):
        plt.close()
        plt.plot(self.weights)
        plt.title('Weight vs Time')
        plt.grid()
        plt.savefig('weight_data.png')

    def plot_avg_data(self):
        plt.close()
        plt.plot(self.avgs)
        plt.title('Average Weight vs Time')
        plt.grid()
        plt.savefig('average_weight_data.png')


async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload='bwws1g7gg43d0k9exdl2aj73hl8zyvappwger45vnbdsh706')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(
            credentials=creds,
            disable_webrtc=True,
            auth_entity='test-bench-main.jrh0bbfyer.viam.cloud'
        )
    )
    return await RobotClient.at_address('localhost:8080', opts)

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
    await stf_06_ip.go_for(100, 20)
    stf_06_ip_return_value = await stf_06_ip.is_moving()
    print(f"STF06-IP is_moving return value: {stf_06_ip_return_value}")

    # Don't forget to close the machine when you're done!
    await robot.close()

    
async def dispense(serving, samples=100, sample_rate=25, outlier_ratio=0.50, rpm=50, step=1000, offset=0, n=10, inc_step=0.25):
    """Function that takes in a serving amount (and other settings) and dispenses that weight
    """
    live_weigh = {'command': 'live-weigh'}

    print('Dispensing... ')

    # Initialize robot, scale, and motor
    robot = await connect()
    scale = Sensor.from_robot(robot, 'phidgets')
    motor = Motor.from_robot(robot, 'STF06-IP')

    def prune(data_set, ratio=outlier_ratio):
        """Function that takes in a data set and returns the average, excluding the amount
        of outliers specified.
        """
        outliers = []
        for _ in range(int(ratio*len(data_set)/2)):
            outliers += [max(data_set), min(data_set)]
        weight = (sum(data_set)-sum(outliers))/(len(data_set)-len(outliers))
        return weight

    # Fills the rolling data set before dispensing begins
    # Consider using .get_readings instead?
    weights = []
    for _ in range(samples):
        reading = await scale.do_command(live_weigh)
        weights += [reading['live-weigh']]
        await asyncio.sleep(1/sample_rate)

    data = Data()
    data.log_weight(weights)

    # Preset rolling window (last_n), avg (last_n's average w/out outliers), initial weight
    last_n = []
    avg = prune(weights)
    init_weight = avg
    target = init_weight-serving

    # Slews motor for absurdly long duration
    await motor.go_for(rpm, 500)

    # Loops through weighing while dispensing w/ p-control
    while avg > target+offset:
        # Takes new weight sample and updates rolling window, avg
        reading = await scale.do_command(live_weigh)
        last_n = last_n[1:] + [reading['live-weigh']]
        avg = prune(last_n)
        # P-control of conveyor speed
        err = (avg-target)/serving
        # await motor.stop()
        new_rpm = max(err*rpm, 10)
        await motor.go_for(new_rpm, 50)
        # await motor.go_for(50, 50)
        await asyncio.sleep(1/sample_rate)
        data.log_avg(avg)
        data.log_weight(reading['live-weigh'])
    
    # Closes out and takes final weight
    await motor.stop()
    end = await scale.get_readings()
    await robot.close()
    # return 'Dispensed ' + str(init_weight-end['weight']) + ' g'
    return data

async def test():
    robot = await connect()
    motor = Motor.from_robot(robot, 'STF06-IP')
    for _ in range(5):
        await motor.go_for(100, 50)
        await motor.stop()
        await asyncio.sleep(1)
        await motor.go_for(200, -50)
        await asyncio.sleep(1)
    await robot.close()

async def weigh():
    robot = await connect()
    scale = Sensor.from_robot(robot, 'phidgets')
    weight = await scale.get_readings()
    print('weight: ', weight['weight'])
    await robot.close()

if __name__ == '__main__':
    # asyncio.run(main())
    msg = asyncio.run(dispense(100))
    msg.plot_weight_data()
    msg.plot_avg_data()
    # print(msg)
    # asyncio.run(test())
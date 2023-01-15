from machine import Pin, ADC, PWM, I2C
from time import sleep


def loop():
    Raindrop_AO = ADC(0)
    while True:
        text = 'Warning!\nFlood warning!'        # show alert information
        adc_Raindrop = Raindrop_AO.read_u16()
        if adc_Raindrop < 30000:
            print("Rain")
        else:
            print("Not Rain")
        sleep(0.5)


if __name__ == '__main__':
    loop()

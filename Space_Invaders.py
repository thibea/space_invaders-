from pyb import SPI,UART, Pin, Timer, LED

numéro_uart = 2

uart = pyb.UART(numéro_uart)
uart.init (115200 , bits = 8 , parity = None , stop = 1)

class Vaisseau:
    def __init__ (self,x,y,skin):
        self.x=x
        self.y=y
        self.skin=skin

Haut=80
large=24
Xmin=1
Ymin=1
Xmax=Haut
Ymax=large
    

NB_Block = 200
X_Right = 205
X_Left = 1
Y_Top = 1
Y_Bottom = 52
Y_Vaisseau = 50

vaisseau=Vaisseau((Xmax+Xmin)//2, Y_Bottom-2, "/~~O~~/")    

class Vaisseau_enemi:
    def __init__(self,x,y,skin,visible):
        self.x=x
        self.y=y
        self.skin=skin
        self.visible=visible
        
def move (x,y):
    uart.write("\x1b[{};{}H".format (y,x))

def clear_ecran ():
    uart.write("\x1b[2J\x1b[?25l")
    
clock_time =0

def clock (timer):
    global clock_time
    clock_time+= 1

t= Timer(4, freq=10)
t.callback(clock)

def borders():
    move(X_Left,Y_Top)
    uart.write("#"* (X_Right-X_Left))
    move(X_Left,Y_Bottom)
    uart.write("#"* (X_Right-X_Left))
    for y in range (Y_Top, Y_Bottom):
        move (X_Left,y)
        uart.write("#")
        move(X_Right, y)
        uart.write("#")

        
def vaisseau_enemi_init (Vaisseau_enemi,x,y,skin):
    Vaisseau_enemi.visible = True
    Vaisseau_enemi.x = x
    Vaisseau_enemi.y = y
    Vaisseau_enemi.skin = "\~~V~~/"

def Vaisseau_enemi_draw (Vaisseau_enemi):
    if Vaisseau_enemi==visible:
        move(Vaisseau_enemi.x, Vaisseau_enemi.y)
        uart.write(Vaisseau_enemi.skin)

def wait_pin_change(pin, etat_souhaite):
    # wait for pin to change value
    # it needs to be stable for a continuous 50ms
    active = 0
    while active < 50:
        if pin.value() == etat_souhaite:
            active += 1
        else:
            active = 0
        delay(1)    
        
CS = Pin("PE3", Pin.OUT_PP)
SPI_1 = SPI(
    1,  # PA5, PA6, PA7
    SPI.MASTER,
    baudrate=50000,
    polarity=0,
    phase=0,
    # firstbit=SPI.MSB,
    # crc=None,
)

def read_reg(addr):
    CS.low()
    SPI_1.send(addr | 0x80)  # 0x80 pour mettre le R/W à 1
    tab_values = SPI_1.recv(1)  # je lis une liste de 1 octet
    CS.high()
    return tab_values[0]

def write_reg(addr, value):
    CS.low()
    SPI_1.send(addr | 0x00)  # write
    SPI_1.send(value)
    CS.high()

def convert_value(high, low):
    value = (high << 8) | low
    if value & (1 << 15):
        # negative number
        value = value - (1 << 16)
    return value*0.06               #lecture en mg

def read_acceleration(base_addr):
    low = read_reg(base_addr)
    high = read_reg(base_addr + 1)
    return convert_value(high, low)

addr_who_am_i = 0x0F
print(read_reg(addr_who_am_i))
addr_ctrl_reg4 = 0x20
write_reg(addr_ctrl_reg4, 0x77)
clear_ecran()
borders()

while True:
    x_accel = read_acceleration(0x28)
    y_accel = read_acceleration(0x2A)

    #print("{:20}, {:20}".format(x_accel, y_accel))
    print(vaisseau.x,vaisseau.y)
    
    seuil = 0x12C           #valeur de 300 mg
    led_px , led_nx  = LED (1) , LED (2)
    
    if x_accel > seuil:
        led_px.on()
        move(vaisseau.x, vaisseau.y)
        uart.write("       ")
        vaisseau.x+=1
        move(vaisseau.x, vaisseau.y)
        uart.write(vaisseau.skin)
    else:
        led_px.off()
        
    if x_accel < -seuil:
        led_nx.on()
        move(vaisseau.x, vaisseau.y)
        uart.write("       ")
        vaisseau.x-=1
        move(vaisseau.x, vaisseau.y)
        uart.write(vaisseau.skin)
    else:
        led_nx.off()
         
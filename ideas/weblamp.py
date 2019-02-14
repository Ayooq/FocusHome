
from flask import Flask, render_template, request

from gpio_iron import FildSwitch

app = Flask(__name__)


fld = FildSwitch()

# GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
# pins = {
   # 24 : {'name' : 'coffee maker', 'state' : GPIO.LOW},
   # 25 : {'name' : 'lamp', 'state' : GPIO.LOW}
   # }

# Set each pin as an output and make it low:
# for pin in pins:
   # GPIO.setup(pin, GPIO.OUT)
   # GPIO.output(pin, GPIO.LOW)

@app.route("/")
def main():
   # For each pin, read the pin state and store it in the pins dictionary:
   for s in fld.keys():
      fld[s].state
      # pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'irons': fld.sub
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   id = changePin
   device = fld[id]
   # Get the device name for the pin being changed:
   # deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      device.on()
      # Save the status message to be passed into the template:
      message = "Включаю " + device.ident
   if action == "off":
      # GPIO.output(changePin, GPIO.LOW)
      device.off()
      message = "Выключаю " + device.ident
   # if action == "toggle":
      # Read the pin and set it to whatever it isn't (that is, toggle it):
      # GPIO.output(changePin, not GPIO.input(changePin))
      # message = "Toggled " + deviceName + "."

   # For each pin, read the pin state and store it in the pins dictionary:
   # For each pin, read the pin state and store it in the pins dictionary:
   for s in fld.keys():
      fld[s].state
      # pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'message': message,
      'irons': fld.sub
      }

   return render_template('main.html', **templateData)

   
if __name__ == "__main__":
   app.rоun(host='127.0.0.1', port=5000, debug=True)
   # app.run(host='0.0.0.0', port=80, debug=True)

import pyautogui as pya
import time

flag = 0
time.sleep(3)

while(True):
	if(not bool(flag)):
		pya.click(636, 966)
		pya.write('Shut the fuck up', interval=0.05)
		pya.press('enter')

	if(flag==2):
		break

	elif(flag==3):
		pya.click(636, 966)
		pya.press('esc')

	pya.click(1368, 758)
	flag = int(input("Enter flag : "))
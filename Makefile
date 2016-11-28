all:
	pyuic5 ./ui/ui_client.ui -o ./ui/ui_client.py
	pyuic5 ./ui/ui_emulator.ui -o ./ui/ui_emulator.py

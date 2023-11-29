package main

import (
	"machine"
	"time"
)

func main() {
	led := machine.GP0
	led.Configure(machine.PinConfig{
		Mode: machine.PinOutput,
	})

	for {
		led.Set(!led.Get()) // toggle LED
		time.Sleep(time.Second / 4)
	}
}

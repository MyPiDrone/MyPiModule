--
--  Copyright (c) Scott Simpson
--
-- 	This program is free software: you can redistribute it and/or modify
--  it under the terms of the GNU General Public License as published by
--  the Free Software Foundation, either version 3 of the License, or
--  (at your option) any later version.
--
--  This program is distributed in the hope that it will be useful,
--  but WITHOUT ANY WARRANTY; without even the implied warranty of
--  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--  GNU General Public License for more details.
--
--  A copy of the GNU General Public License is available at <http://www.gnu.org/licenses/>.0139261378


--------------------------------------------------------------------------------------------------

local function drawTopPanel()
    lcd.drawFilledRectangle(0, 0, 212, 9, 0)

    local flightModeNumber = getValue("Fuel") + 1
    if flightModeNumber < 1 or flightModeNumber > 17 then
        flightModeNumber = 13
    end

    lcd.drawText(1, 1, FlightMode[flightModeNumber].Name, INVERS)

    lcd.drawTimer(lcd.getLastPos() + 10, 1, model.getTimer(0).value, INVERS)

    lcd.drawText(lcd.getLastPos() + 10, 1, "TX:", INVERS)
--  lcd.drawNumber(lcd.getLastPos() + 16, 1, getValue("tx-voltage"), 0+PREC1+INVERS)
--    lcd.drawNumber(lcd.getLastPos() + 16, 1, getValue("Batt"), 0+PREC1+INVERS)
   lcd.drawNumber(lcd.getLastPos() + 16, 1, getValue("tx-voltage") * 10, 0+PREC1+INVERS)

    lcd.drawText(lcd.getLastPos(), 1, "v", INVERS)

    lcd.drawText(lcd.getLastPos() + 12, 1, "rssi:", INVERS)
    lcd.drawNumber(lcd.getLastPos() + 10, 1, getValue("RSSI"), 0+INVERS)
end

local function drawBottomPanel()
    local footerMessage = getTextMessage()
    lcd.drawFilledRectangle(0, 54, 212, 63, 0)
    lcd.drawText(2, 55, footerMessage, INVERS)
end

local function background()
end

local function run(event)
    local loopStartTime = getTime()
    if loopStartTime > (lastTime + 100) then
        checkForNewMessage()
        lastTime = loopStartTime
    end
    checkForNewMessage()

    lcd.clear()
    drawTopPanel()
    local i
    local row = 1
    for i = messageFirst, messageNext - 1, 1 do
--      lcd.drawText(1, row * 9, i .. " " .. row .. " " .. messageFirst .. " " .. messageNext .. messageArray[(i % MESSAGEBUFFERSIZE) + 1], 0)
        lcd.drawText(1, row * 9, messageArray[(i % MESSAGEBUFFERSIZE) + 1], 0)
        if (row == 5) then
		   row= 1
		else
		   row = row + 1
		end
    end
    local coords =  getValue("GPS")
    if (type(coords) == "table") then
      lcd.drawText(1, 55, "Latitude ", INVERS)
      lcd.drawText(lcd.getLastPos(), 55, coords["lat"], INVERS)
      lcd.drawText(lcd.getLastPos(), 55, "Longitude ", INVERS)
      lcd.drawText(lcd.getLastPos(), 55, coords["lon"], INVERS)
    else
      lcd.drawText(1, 55, "No Longitude Sensor ", INVERS)
      lcd.drawText(lcd.getLastPos() , 55, "No Latitude Sensor", INVERS)
    end

end

return {run=run, background=background}

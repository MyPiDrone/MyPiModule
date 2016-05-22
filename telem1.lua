----
----  Copyright (c) Scott Simpson
----
---- 	This program is free software: you can redistribute it and/or modify
----  it under the terms of the GNU General Public License as published by
----  the Free Software Foundation, either version 3 of the License, or
----  (at your option) any later version.
----
----  This program is distributed in the hope that it will be useful,
----  but WITHOUT ANY WARRANTY; without even the implied warranty of
----  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
----  GNU General Public License for more details.
----
----  A copy of the GNU General Public License is available at <http://www.gnu.org/licenses/>.
----
--
modelInfo = model.getInfo()
modelName = modelInfo.name
--scriptDirectory = "/SCRIPTS/" .. modelName
--
--RIGHTPX = 212
--BOTTOMPX = 63
--
FlightMode = {}
Severity={}
AsciiMap={}

local function initialize()
  local i
  for i=1, 17 do
    FlightMode[i] = {}
    FlightMode[i].Name=""
  end

  FlightMode[1].Name="Stabilize"
  FlightMode[2].Name="Acro"
  FlightMode[3].Name="Altitude Hold"
  FlightMode[4].Name="Auto"
  FlightMode[5].Name="Guided"
  FlightMode[6].Name="Loiter"
  FlightMode[7].Name="Return to launch"
  FlightMode[8].Name="Circle"
  FlightMode[9].Name="Invalid Mode"
  FlightMode[10].Name="Land"
  FlightMode[11].Name="Optical Loiter"
  FlightMode[12].Name="Drift"
  FlightMode[13].Name="Invalid Mode"
  FlightMode[14].Name="Sport"
  FlightMode[15].Name="Flip Mode"
  FlightMode[16].Name="Auto Tune"
  FlightMode[17].Name="Position Hold"

  for i=1,9 do
    Severity[i]={}
    Severity[i].Name=""
    Severity[i].Sound="/SOUNDS/en/ER"..(i-2)..".wav"
  end

  Severity[2].Name="Emergency"
  Severity[3].Name="Alert"
  Severity[4].Name="Critical"
  Severity[5].Name="Error"
  Severity[6].Name="Warning"
  Severity[7].Name="Notice"
  Severity[8].Name="Info"
  Severity[9].Name="Debug"

  AsciiMap[1] ="A"
  AsciiMap[2] ="B"
  AsciiMap[3] ="C"
  AsciiMap[4] ="D"
  AsciiMap[5] ="E"
  AsciiMap[6] ="F"
  AsciiMap[7] ="G"
  AsciiMap[8] ="H"
  AsciiMap[9] ="I"
  AsciiMap[10] ="J"
  AsciiMap[11] ="K"
  AsciiMap[12] ="L"
  AsciiMap[13] ="M"
  AsciiMap[14] ="N"
  AsciiMap[15] ="O"
  AsciiMap[16] ="P"
  AsciiMap[17] ="Q"
  AsciiMap[18] ="R"
  AsciiMap[19] ="S"
  AsciiMap[20] ="T"
  AsciiMap[21] ="U"
  AsciiMap[22] ="V"
  AsciiMap[23] ="W"
  AsciiMap[24] ="X"
  AsciiMap[25] ="Y"
  AsciiMap[26] ="Z"
end

initialize()

function char(c)
  if c >= 48 and c <= 57 then
    return "0" + (c - 48)
  elseif c >= 65 and c <= 90 then
    return AsciiMap[c - 64]
  elseif c >= 97 and c <= 122 then
    return AsciiMap[c - 96]
  elseif c == 32 then
    return " "
  elseif c == 46 then
    return "."
  else
    return ""
  end
end

messageBuffer = ""
messageBufferSize = 0
previousMessageWord = 0
footerMessage = "NO MESSAGE"
messagePriority = -1
armingHeading = 0
arming_coords = 0
previous_arming_state = 0


function getTextMessage()
  local returnValue = ""
  local messageWord = getValue("RPM") / 2 --correct for default blade number 1 in 2.1.*

  if messageWord ~= previousMessageWord then
    local highByte = bit32.rshift(messageWord, 7)
    highByte = bit32.band(highByte, 127)
    local lowByte = bit32.band(messageWord, 127)

    if highByte ~= 0 then
      if highByte >= 48 and highByte <= 57 and messageBuffer == "" then
        messagePriority = highByte - 48
      else
        messageBuffer = messageBuffer .. char(highByte)
        messageBufferSize = messageBufferSize + 1
      end
      if lowByte ~= 0 then
        messageBuffer = messageBuffer .. char(lowByte)
        messageBufferSize = messageBufferSize + 1
      end
    end
    if highByte == 0 or lowByte == 0 then
      returnValue = messageBuffer
      messageBuffer = ""
      messageBufferSize = 0
    end
    previousMessageWord = messageWord
  end
  return returnValue
end

MESSAGEBUFFERSIZE = 5
messageArray = {}
messageFirst = 0
messageNext = 0
messageLatestTimestamp = 0

function getLatestMessage()
  if messageFirst == messageNext then
    return ""
  end
  return messageArray[((messageNext - 1) % MESSAGEBUFFERSIZE) + 1]
end
--
function checkForNewMessage()
  local msg = getTextMessage()
  if msg ~= "" then
    if msg ~= getLatestMessage() then
      messageArray[(messageNext % MESSAGEBUFFERSIZE) + 1] = msg
      messageNext = messageNext + 1
      if (messageNext - messageFirst) >= MESSAGEBUFFERSIZE then
        messageFirst = messageNext - MESSAGEBUFFERSIZE
      end
      messageLatestTimestamp = getTime()
    end
  end
end

function getXYAtAngle(x, y, angle, length)
  if angle < 0 then
    angle = angle + 360
  elseif angle >= 360 then
    angle = angle - 360
  end
  local x2 = x + math.sin(math.rad(angle)) * length
  local y2 = y - math.cos(math.rad(angle)) * length
  return x2, y2
end

local function drawLineAtAngle(x, y, r1, r2, angle)
  local xStart, yStart = getXYAtAngle(x, y, angle, r1)
  local xEnd, yEnd = getXYAtAngle(x, y, angle, r2)
  lcd.drawLine(xStart, yStart, xEnd, yEnd, SOLID, FORCE)
end

---------------------------------------------------------------------------------------------------

function getDirectionFromTo(fromLat, fromLon, toLat, toLon)
  if(fromLat == toLat and fromLon == toLon) then
    return -1
  end
  local z1 = math.sin(math.rad(toLon) - math.rad(fromLon)) * math.cos(math.rad(toLat))
  local z2 = math.cos(math.rad(fromLat)) * math.sin(math.rad(toLat)) - math.sin(math.rad(fromLat)) * math.cos(math.rad(toLat)) * math.cos(math.rad(toLon) - math.rad(fromLon))
  local directionTo = math.deg(math.atan2(z1, z2))
  if directionTo < 0 then
    directionTo=directionTo+360
  end
  return directionTo
end

lastTime = 0
previousVehicleLat1 = 0
previousVehicleLon1 = 0
previousVehicleLat2 = 0
previousVehicleLon2 = 0
vehicleGroundDirection = -1

function updateGroundDirection()
  local coords =  getValue("GPS")
  if (type(coords) == "table") then
    local currentVehicleLat = coords["lat"]
    local currentVehicleLon = coords["lon"]
    if currentVehicleLat~=0 and currentVehicleLon~=0 and previousVehicleLat2~=0 and previousVehicleLon2~=0 then
      vehicleGroundDirection = getDirectionFromTo(previousVehicleLat2, previousVehicleLon2, currentVehicleLat, currentVehicleLon)
    end
    previousVehicleLat2 = previousVehicleLat1
    previousVehicleLon2 = previousVehicleLon1
    previousVehicleLat1 = currentVehicleLat
    previousVehicleLon1 = currentVehicleLon
  end
end

function getVehicleGroundDirection()
  return vehicleGroundDirection
end

----------------------------------------------------------------------------------------------------

local function drawBatteryVoltage(x,y)
  local batteryVoltage=getValue("VFAS") * 10
  lcd.drawNumber(x,y,batteryVoltage, MIDSIZE+PREC1)
  lcd.drawText(lcd.getLastPos(),y+5,"V",SMLSIZE)
end

local function drawCurrent(x,y)
  local current=getValue("Curr") * 10
  lcd.drawNumber(x,y,current, MIDSIZE+PREC1)
  lcd.drawText(lcd.getLastPos(),y+5,"A",SMLSIZE)
end

local function drawTotalCurrent(x,y)
  local totalCurrent = getValue("AccX")
  lcd.drawNumber(x, y, totalCurrent, MIDSIZE)
  lcd.drawText(lcd.getLastPos(), y+5, "% Bat", SMLSIZE)
end

local function drawSpeed(x,y)
  local speed = getValue("GSpd")
  lcd.drawText(x, y + 5, "Spd", SMLSIZE)
  lcd.drawNumber(x + 37, y, speed, MIDSIZE)
  local t = lcd.getLastPos() + 1
  lcd.drawText(t, y, "km", SMLSIZE)
  lcd.drawText(t, y+5, "hr", SMLSIZE)
end

local function drawAltitude(x, y)
  local altitude = getValue("Alt")
  lcd.drawText(x, y + 5, "B.Alt", SMLSIZE)
  lcd.drawNumber(x + 36, y, altitude, MIDSIZE)
  local t = lcd.getLastPos() + 1
  lcd.drawText(t, y + 5, "m", SMLSIZE)
end

local function drawDistance(x, y)
  lcd.drawText(x, y + 5, "Dst", SMLSIZE)
  local distance = 0
  coords = getValue("GPS")
  local arming_state = getValue("AccY")
  if (arming_state ~= 0) then
    if (previous_arming_state == 0) then
      previous_arming_state = 1
      if (type(coords) == "table") then
        arming_coords = coords
      end
    end
  else
    arming_coords = 0
    previous_arming_state = 0
  end

  if (type(coords) == "table" and type(arming_coords) == "table" and arming_state ~= 0) then
    local EARTH_RADIUS = 111194 -- meters
    local lat_dist = math.abs(arming_coords["lat"] - coords["lat"]) * EARTH_RADIUS
    lat_dist = lat_dist * lat_dist
    local long_dist = math.abs(arming_coords["lon"] - coords["lon"]) * EARTH_RADIUS
    long_dist = long_dist * long_dist
    distance = math.sqrt(lat_dist + long_dist + getValue("Alt") * getValue("Alt"))
    if distance >= 100.0 then
      distance = distance / 1000.0
      lcd.drawNumber(x + 36, y, distance, MIDSIZE + PREC1)
      local t = lcd.getLastPos() + 1
      lcd.drawText(t, y + 5, "Km", SMLSIZE)
    else
      lcd.drawNumber(x + 36, y, distance, MIDSIZE + PREC1)
      local t = lcd.getLastPos() + 1
      lcd.drawText(t, y + 5, "m", SMLSIZE)
    end
else
    local t = lcd.getLastPos() + 3
    lcd.drawText(t, y + 5, "None  ", SMLSIZE)
  end
end

local function drawHdop(x,y)
  local hdop = getValue("A2") * 4 * 255/13.2 / 100
  if hdop > 9.9 then
    --hdop = 9.9*10
    lcd.drawText(x-24, y+3, ">", SMLSIZE)
  end
  lcd.drawNumber (x, y, hdop * 10, PREC1 + MIDSIZE)
  local t = lcd.getLastPos() + 1
  lcd.drawText(t, y, "hd", SMLSIZE)
  lcd.drawText(t, y + 6, "op", SMLSIZE)
end

local function drawSats(x, y)
  local satValue = getValue("Tmp1")
  local numSats = (satValue - (satValue % 10)) /10
  local lock = satValue % 10
  if lock >= 3 then
    lcd.drawNumber(x + 6, y, numSats, MIDSIZE)
    lcd.drawText(x + 7, y + 5, "sats", SMLSIZE)
  elseif lock == 2 then
    lcd.drawText(x + 8, y, "2D", MIDSIZE)
  elseif lock == 1 then
    lcd.drawText(x, y + 5, "Search", SMLSIZE)
  elseif lock == 0 then
    lcd.drawText(x, y + 5, "No Fix", SMLSIZE)
  end
end

local function getHeading()
  return getValue("Hdg")
end

local function drawHeadingHud(x, y)
  local arrowSide = 5
  local arrowTail = 5
  local arrowLength = 16
  local arrowSideAngle = 120
  local headingHudOuterRadius = 15
  local arming_state = getValue("AccY")

  if arming_state == 0 then
    armingHeading = getHeading()
    relativeHeading = armingHeading
  else
    relativeHeading = getHeading() - armingHeading
  end

  local xTail, yTail = getXYAtAngle(x, y, relativeHeading - 180, arrowTail)
  local xLeft, yLeft = getXYAtAngle(xTail, yTail, relativeHeading-arrowSideAngle, arrowSide)
  local xRight, yRight = getXYAtAngle(xTail, yTail, relativeHeading+arrowSideAngle, arrowSide)
  local xNose, yNose = getXYAtAngle(xTail, yTail, relativeHeading, arrowLength)
  lcd.drawLine(xTail, yTail, xLeft, yLeft, SOLID, FORCE)
  lcd.drawLine(xLeft, yLeft, xNose, yNose, SOLID, FORCE)
  lcd.drawLine(xTail, yTail, xRight, yRight, SOLID, FORCE)
  lcd.drawLine(xRight, yRight, xNose, yNose, SOLID, FORCE)


  if getValue("GSpd") > 0 then
    local relativeGroundDirection = getVehicleGroundDirection()
    drawLineAtAngle(x, y, 0, headingHudOuterRadius, relativeGroundDirection)
  end
end

local function drawTopPanel()
  lcd.drawFilledRectangle(0, 0, 212, 9, 0)
  local flightModeNumber = getValue("Fuel") + 1
  if flightModeNumber < 1 or flightModeNumber > 17 then
    flightModeNumber = 13
  end
  lcd.drawText(1, 1, FlightMode[flightModeNumber].Name, INVERS)

  lcd.drawTimer(lcd.getLastPos() + 10, 1, model.getTimer(0).value, INVERS)

  lcd.drawText(lcd.getLastPos() + 10, 1, "TX:", INVERS)
  lcd.drawNumber(lcd.getLastPos() + 16, 1, getValue("tx-voltage") * 10, PREC1+INVERS)

  lcd.drawText(lcd.getLastPos(), 1, "V", INVERS)

  lcd.drawText(lcd.getLastPos() + 10, 1, "RSSI:", INVERS)
  lcd.drawNumber(lcd.getLastPos() + 16, 1, getValue("RSSI"), 0+INVERS)
end
--
local function drawBottomPanel()
  lcd.drawFilledRectangle(0, 54, 212, 63, 0)
  if getTime() < (messageLatestTimestamp + 1000) then
    local footerMessage = getLatestMessage()
    lcd.drawText(2, 55, footerMessage, INVERS)
  else
    local arming_state = getValue("AccY")
    if arming_state ~= 0 then
      lcd.drawText(2, 55, "System ARMED", INVERS)
    else
      lcd.drawText(2, 55, "System NOT armed", INVERS)
    end
    lcd.drawText(lcd.getLastPos() + 10, 55, "Hdg:", INVERS)
    lcd.drawNumber(lcd.getLastPos() + 16, 55, getHeading(), INVERS)
  end
end
--
--local function background()
--end
--
local function run(event)
  local loopStartTime = getTime()
  if loopStartTime > (lastTime + 50) then
    updateGroundDirection()
    lastTime = loopStartTime
  end

  lcd.clear()
  checkForNewMessage()

  drawTopPanel()
  drawBottomPanel()

  drawBatteryVoltage(32, 12)
  drawCurrent(32, 26)
  drawTotalCurrent(32, 40)

  drawSats(72, 40)
  drawHdop(130, 40)

  drawHeadingHud(107, 26)

  drawSpeed(159, 12)
  drawAltitude(160, 26)
  drawDistance(160, 40)
end


return { run=run }
--return {run=run, init=initialize, background=background}

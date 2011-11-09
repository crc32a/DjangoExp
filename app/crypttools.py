#!/usr/bin/python

import Crypto.Hash.SHA256
import Crypto.Cipher.AES
import Crypto.Hash.SHA
import Crypto.Hash.MD5
import cPickle
import pickle
import string
import random
import base64
import crypt
import time
import zlib
import md5
import os

LEFT_DIR   = 1
RIGHT_DIR  = 2
DEFAULTBLOCKSIZE = 1024*64
mosso_hash = Crypto.Hash.SHA.new("Mosso's Secret").digest()

#passcrypt and passcrypt_md5 from Christopher Arndts authlib.py
#module found at http://www.chrisarndt.de/en/software/python/#auth

des_salt_str  = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
des_salt_str += "abcdefghijklmnopqrstuvwxyz"
DES_SALT = [ch for ch in des_salt_str]

rnd = random.Random()

def rnddesch():
    return rnd.choice(DES_SALT)

def passcrypt(passwd, salt=None, method='des', magic='$1$'):
    """Encrypt a string according to rules in crypt(3)."""

    if method.lower() == 'des':
        if not salt:
            salt = rnddesch() + rnddesch()
        return crypt.crypt(passwd, salt)
    elif method.lower() == 'md5':
        return passcrypt_md5(passwd, salt, magic)
    elif method.lower() == 'clear':
        return passwd


def _to64(v, n):
    r = ''
    while (n-1 >= 0):
        r = r + DES_SALT[v & 0x3F]
        v = v >> 6
        n = n - 1
    return r

def passcrypt_md5(passwd, salt=None, magic='$1$'):
    """Encrypt passwd with MD5 algorithm."""

    if not salt:
        salt = repr(int(time.time()))[-8:]
    elif salt[:len(magic)] == magic:
        # remove magic from salt if present
        salt = salt[len(magic):]

    # salt only goes up to first '$'
    salt = string.split(salt, '$')[0]
    # limit length of salt to 8
    salt = salt[:8]

    ctx = md5.new(passwd)
    ctx.update(magic)
    ctx.update(salt)

    ctx1 = md5.new(passwd)
    ctx1.update(salt)
    ctx1.update(passwd)

    final = ctx1.digest()

    for i in range(len(passwd), 0 , -16):
        if i > 16:
            ctx.update(final)
        else:
            ctx.update(final[:i])

    i = len(passwd)
    while i:
        if i & 1:
            ctx.update('\0')
        else:
            ctx.update(passwd[:1])
        i = i >> 1
    final = ctx.digest()

    for i in range(1000):
        ctx1 = md5.new()
        if i & 1:
            ctx1.update(passwd)
        else:
            ctx1.update(final)
        if i % 3: ctx1.update(salt)
        if i % 7: ctx1.update(passwd)
        if i & 1:
            ctx1.update(final)
        else:
            ctx1.update(passwd)
        final = ctx1.digest()
    rv = magic + salt + '$'
    final = map(ord, final)
    l = (final[0] << 16) + (final[6] << 8) + final[12]
    rv = rv + _to64(l, 4)
    l = (final[1] << 16) + (final[7] << 8) + final[13]
    rv = rv + _to64(l, 4)
    l = (final[2] << 16) + (final[8] << 8) + final[14]
    rv = rv + _to64(l, 4)
    l = (final[3] << 16) + (final[9] << 8) + final[15]
    rv = rv + _to64(l, 4)
    l = (final[4] << 16) + (final[10] << 8) + final[5]
    rv = rv + _to64(l, 4)
    l = final[11]
    rv = rv + _to64(l, 2)
    return rv


def pad(digits,ch,val,**kargs):
  str_out=str(val)
  if not "side" in kargs:
    kargs["side"]=LEFT_DIR
  if kargs["side"]==LEFT_DIR or kargs["side"]=="LEFT_DIR":
    for i in xrange(0,digits-len(str_out)):
      str_out = ch + str_out
    return str_out
  if kargs["side"]==RIGHT_DIR or kargs["side"]=="RIGHT_DIR":
    for i in xrange(0,digits-len(str_out)):
      str_out = str_out + ch
    return str_out

def file_md5sum(file_name,blocksize=DEFAULTBLOCKSIZE):
    file_path = os.path.expanduser(file_name)
    fp = open(file_path,"r")
    while True:
        data = fp.read(block)
        if len(data) == 0:
            break
        m.update(data)
    fp.close()
    return m.hexdigest()

        
def md5sum(data_str):
    m=md5.new()
    m.update(data)
    return m.hexdigest()

def random_iv(nch):
    return string.join([chr(rnd.randint(0,255)) for x in xrange(0,nch)],"")

class AesWrapperException:
    pass

class MsgTooBig(AesWrapperException):
    def __repr__(self):
        return "Msg to big for encryption"

class InvalidKey(AesWrapperException):
    def __repr__(self):
        return "EncryptionKey/DecryptionKey don't match"

class UnknownPickleMethod(AesWrapperException):
    def __repr__(self):
        return "Unknown pickle method"

def toHex(str_in):
    out = ""
    cmap = dict(zip([i for i in xrange(0,16)],[ch for ch in "0123456789abcdef"]))
    for ch in str_in:
        i = ord(ch)
        out += cmap[(i>>4)]
        out += cmap[(i%16)]
    return out
        
class Aes_wrapper(object):
  def __init__(self,key_in,len_bytes=4):
    if isinstance(key_in,unicode):
        key_in = key_in.encode("utf-8")
    self.key = Crypto.Hash.SHA.new(key_in).digest()[0:16]
    self.mode = Crypto.Cipher.AES.MODE_CBC
    self.aes = Crypto.Cipher.AES.new(self.key,self.mode)
    self.len_bytes = len_bytes
    self.max_size = 2**(len_bytes*8) - 1
    self.len_nibbles = len_bytes * 2

  def dumps(self,obj,**kw):
      if "method" in kw:
          if kw["method"] == "pickle":
              pdump = pickle.dumps(obj)
          elif kw["method"] == "cpickle":
              pdump = cPickle.dumps(obj)
          else:
              raise UnknownPickleMethod
              return Nonw
      else:
          pdump = cPickle.dumps(obj) #use pickle by default

      if "compress" in kw and kw["compress"] == True:
          pdump = zlib.compress(pdump,9)
      cdump = self.encrypt(pdump)
      return cdump

  def loads(self,cdump,**kw):
      pdump = self.decrypt(cdump)
      if "compress" in kw and kw["compress"] == True:
          pdump = zlib.decompress(pdump)

      if "method" in kw:
          if kw["method"]=="cpickle":
              obj = cPickle.loads(pdump)
              return obj
          elif kw["method"]=="pickle":
              obj = pickle.loads(pdump)
              return obj
          else:
              raise UnknownPickleMethod
              return None
      else:
          obj = cPickle.loads(pdump)
          return obj

     
  def dump(self,obj,fp,**kw):
      cdump = self.dumps(obj,**kw)
      fp.write(cdump)
      fp.close()

  def load(self,fp,**kw):
      cdump = fp.read()
      obj = self.loads(cdump,**kw)
      return obj

  def load_file(self,file_name,**kw):
      path = os.path.expanduser(file_name)
      fp = open(path,"r")
      obj = self.load(fp,**kw)
      fp.close()
      return obj

  def save_file(self,obj,file_name,**kw):
      path = os.path.expanduser(file_name)
      fp = open(path,"w")
      self.dump(obj,fp,**kw)
      fp.close()

  def encrypt(self,msg_in):
    if len(msg_in)>self.max_size:
      raise MsgTooBig
      return None
    length   = hex(len(msg_in))[2:]
    msg_out  = mosso_hash
    msg_out += pad(self.len_nibbles,'0',length)
    msg_out += msg_in
    while len(msg_out)%16 != 0:
      msg_out += " "
    ctext = self.aes.encrypt(msg_out)
    return ctext

  def decrypt(self,cmsg):
    lnibbles = self.len_nibbles
    hash_in = self.aes.decrypt(cmsg)[:len(mosso_hash)]
    if hash_in != mosso_hash:
        raise InvalidKey
    ptext   = self.aes.decrypt(cmsg)[len(mosso_hash):]
    try:
      length  = int(ptext[0:lnibbles],16)
    except:
      return None
    msg_out = ptext[lnibbles:lnibbles+length]
    return msg_out

  def b64encrypt(self,msg_in):
    ctext = base64.standard_b64encode(self.encrypt(msg_in))
    return ctext

  def b64decrypt(self,cmsg):
    ptext = self.decrypt(base64.standard_b64decode(cmsg))
    return ptext

def aes_encrypt(ptext,key):
    aes = Aes_wrapper(key,len_bytes=2)
    iv = random_iv(4)
    msg = iv + zlib.compress(ptext,9)
    ctext = aes.encrypt(msg)
    return ctext

def aes_decrypt(ctext,key):
    aes = Aes_wrapper(key,len_bytes=2)
    msg = aes.decrypt(ctext)
    ptext = zlib.decompress(msg[4:])
    return ptext



def aes_b64encrypt(ptext,key,zlib=False,iv=32):
    aes = Aes_wrapper(key,len_bytes=2)
    iv = random_iv(iv)
    if zlib:
        msg = iv + zlib.compress(ptext,9)
    else:
        msg = iv + ptext
    ctext = aes.b64encrypt(msg)
    return ctext

def aes_b64decrypt(ctext,key,zlib=False,iv=32):
    aes = Aes_wrapper(key,len_bytes=2)
    msg = aes.b64decrypt(ctext)
    if zlib:
        ptext = zlib.decompress(msg[iv:])
    else:
        ptext = msg[iv:]
    return ptext

def sha256(str_in,hex=True):
    if hex:
        sum = Crypto.Hash.SHA256.new(str_in).hexdigest()
    else:
        sum = Crypto.Hash.SHA256.new(str_in).digest()
    return sum


def b64decode(str_in):
    str_out = base64.standard_b64decode(str_in)
    return str_out

def b64encode(str_in):
    str_out = base64.standard_b64encode(str_in)
    return str_out

import sys
import platform
from base64 import b64encode, b64decode
import collections
import hashlib
import hmac
import json
import os
import socket
import subprocess
import sys
import tempfile
import urllib.parse
import time
import http.client
import requests
from enum import Enum

HMAC_HEADER = 'X-Ycm-Hmac'
HMAC_SECRET_LENGTH = 16
SERVER_IDLE_SUICIDE_SECONDS = 10800
MAX_SERVER_WAIT_TIME_SECONDS = 5

INCLUDE_YCMD_OUTPUT = False
DEFINED_SUBCOMMANDS_HANDLER = '/defined_subcommands'
CODE_COMPLETIONS_HANDLER = '/completions'
COMPLETER_COMMANDS_HANDLER = '/run_completer_command'
EVENT_HANDLER = '/event_notification'
EXTRA_CONF_HANDLER = '/load_extra_conf_file'
DIR_OF_THIS_SCRIPT = os.path.dirname( os.path.abspath( __file__ ) )
PATH_TO_YCMD = os.path.join( DIR_OF_THIS_SCRIPT, '..', 'ycmd' )
PATH_TO_EXTRA_CONF = os.path.join( DIR_OF_THIS_SCRIPT, '.ycm_extra_conf.py' )


class Event( Enum ):
  FileReadyToParse = 1
  BufferUnload = 2
  BufferVisit = 3
  InsertLeave = 4
  CurrentIdentifierFinished = 5


class YcmdHandle( object ):
  def __init__( self, popen_handle, port, hmac_secret ):
    self._popen_handle = popen_handle
    self._port = port
    self._hmac_secret = hmac_secret
    self._server_location = 'http://127.0.0.1:' + str( port )


  @classmethod
  def StartYcmdAndReturnHandle( cls ):
    prepared_options = DefaultSettings()
    hmac_secret = os.urandom( HMAC_SECRET_LENGTH )
    prepared_options[ 'hmac_secret' ] = str( b64encode( hmac_secret ), 'utf-8' )

    # The temp options file is deleted by ycmd during startup
    with tempfile.NamedTemporaryFile( mode = 'w+', delete = False ) \
        as options_file:
      json.dump( prepared_options, options_file )
      server_port = GetUnusedLocalhostPort()
      ycmd_args = [ 'python2',
                    PATH_TO_YCMD,
                    '--port={0}'.format( server_port ),
                    '--options_file={0}'.format( options_file.name ),
                    '--idle_suicide_seconds={0}'.format(
                      SERVER_IDLE_SUICIDE_SECONDS ) ]

    std_handles = None if INCLUDE_YCMD_OUTPUT else subprocess.PIPE
    child_handle = subprocess.Popen( ycmd_args,
                                     stdout = std_handles,
                                     stderr = std_handles )
    return cls( child_handle, server_port, hmac_secret )


  def IsAlive( self ):
    returncode = self._popen_handle.poll()
    return returncode is None


  def IsReady( self, include_subservers = False ):
    if not self.IsAlive():
      return False
    params = { 'include_subservers': 1 } if include_subservers else None
    response = self.GetFromHandler( 'ready', params )
    response.raise_for_status()
    return response.json()


  def Shutdown( self ):
    if self.IsAlive():
      self._popen_handle.terminate()


  def PostToHandlerAndLog( self, handler, data ):
    self._CallHttpie( 'post', handler, data )


  def GetFromHandlerAndLog( self, handler ):
    self._CallHttpie( 'get', handler )


  def GetFromHandler( self, handler, params = None ):
    request_uri = self._BuildUri( handler )
    extra_headers = self._ExtraHeaders(
        'GET', urllib.parse.urlparse( request_uri ).path, '' )
    response = requests.get( request_uri,
                             headers = extra_headers,
                             params = params )
    self._ValidateResponseObject( response )
    return response

  def SendCodeCompletionRequest( self,
                                 test_filename,
                                 filetype,
                                 line_num,
                                 column_num ):
    request_json = BuildRequestData( test_filename = test_filename,
                                     filetype = filetype,
                                     line_num = line_num,
                                     column_num = column_num )
    print( '==== Sending code-completion request ====' )
    self.PostToHandlerAndLog( CODE_COMPLETIONS_HANDLER, request_json )

  def SendEventNotification( self,
                             event_enum,
                             test_filename,
                             filetype,
                             line_num = 1,
                             column_num = 1,
                             extra_data = None ):
    request_json = BuildRequestData( test_filename = test_filename,
                                     filetype = filetype,
                                     line_num = line_num,
                                     column_num = column_num )
    if extra_data:
      request_json.update( extra_data )
    request_json[ 'event_name' ] = event_enum.name
    print( '==== Sending event notification ====' )
    self.PostToHandlerAndLog( EVENT_HANDLER, request_json )


  def LoadExtraConfFile( self, extra_conf_filename ):
    request_json = { 'filepath': extra_conf_filename }
    self.PostToHandlerAndLog( EXTRA_CONF_HANDLER, request_json )


  def WaitUntilReady( self, include_subservers = False ):
    total_slept = 0
    time.sleep( 0.5 )
    total_slept += 0.5
    while True:
      try:
        if total_slept > MAX_SERVER_WAIT_TIME_SECONDS:
          raise RuntimeError(
              'waited for the server for {0} seconds, aborting'.format(
                    MAX_SERVER_WAIT_TIME_SECONDS ) )

        if self.IsReady( include_subservers ):
          return
      except requests.exceptions.ConnectionError:
        pass
      finally:
        time.sleep( 0.1 )
        total_slept += 0.1


  def _ExtraHeaders( self, method, path, body ):
    return { HMAC_HEADER: self._HmacForRequest( method, path, body ) }


  def _HmacForRequest( self, method, path, body ):
    return str( b64encode( CreateRequestHmac( method, path, body,
                                              self._hmac_secret ) ), 'utf8' )


  def _BuildUri( self, handler ):
    return urllib.parse.urljoin( self._server_location, handler )


  def _ValidateResponseObject( self, response ):
    if not ContentHmacValid(
        response.content,
        b64decode( response.headers[ HMAC_HEADER ] ),
        self._hmac_secret ):
      raise RuntimeError( 'Received invalid HMAC for response!' )
    return True

  def _CallHttpie( self, method, handler, data = None ):
    method = method.upper()
    request_uri = self._BuildUri( handler )
    args = [ 'http', '-v', method, request_uri ]
    if isinstance( data, collections.Mapping ):
      args.append( 'content-type:application/json' )
      data = ToUtf8Json( data )

    hmac = self._HmacForRequest( method,
                                 urllib.parse.urlparse( request_uri ).path,
                                 data )
    args.append( HMAC_HEADER + ':' + hmac )
    if method == 'GET':
      popen = subprocess.Popen( args )
    else:
      popen = subprocess.Popen( args, stdin = subprocess.PIPE )
      popen.communicate( data )
    popen.wait()



def ToBytes( value ):
  if isinstance( value, bytes ):
    return value
  if isinstance( value, int ):
    value = str( value )
  return bytes( value, encoding = 'utf-8' )


def ContentHmacValid( content, hmac, hmac_secret ):
  return SecureBytesEqual( CreateHmac( content, hmac_secret ), hmac )


def CreateRequestHmac( method, path, body, hmac_secret ):
  method = ToBytes( method )
  path = ToBytes( path )
  body = ToBytes( body )
  hmac_secret = ToBytes( hmac_secret )

  method_hmac = CreateHmac( method, hmac_secret )
  path_hmac = CreateHmac( path, hmac_secret )
  body_hmac = CreateHmac( body, hmac_secret )
  joined_hmac_input = bytes().join( ( method_hmac, path_hmac, body_hmac ) )
  return CreateHmac( joined_hmac_input, hmac_secret )


def CreateHmac( content, hmac_secret ):
  return bytes( hmac.new( ToBytes( hmac_secret ),
                          msg = ToBytes( content ),
                          digestmod = hashlib.sha256 ).digest() )


def SecureBytesEqual( a, b ):
  if type( a ) != bytes or type( b ) != bytes:
    raise TypeError( "inputs must be bytes instances" )

  if len( a ) != len( b ):
    return False

  result = 0

  for x, y in zip( a, b ):
    result |= x ^ y

  return result == 0


def RecursiveEncodeUnicodeToUtf8( value ):
  if isinstance( value, str ):
    return value.encode( 'utf8' )
  if isinstance( value, bytes ):
    return value
  elif isinstance( value, collections.Mapping ):
    return dict( list(
      map( RecursiveEncodeUnicodeToUtf8, iter( value.items() ) ) ) )
  elif isinstance( value, collections.Iterable ):
    return type( value )( list( map( RecursiveEncodeUnicodeToUtf8, value ) ) )
  else:
    return value


def ToUtf8Json( data ):
  return json.dumps( data, ensure_ascii = False ).encode( 'utf8' )


def PathToTestFile( filename ):
  return os.path.join( DIR_OF_THIS_SCRIPT, 'samples', filename )


def DefaultSettings():
  default_options_path = os.path.join( DIR_OF_THIS_SCRIPT,
                                       '..',
                                      'ycmd',
                                      'default_settings.json' )

  with open( default_options_path ) as f:
    return json.loads( f.read() )


def GetUnusedLocalhostPort():
  sock = socket.socket()

  sock.bind( ( '', 0 ) )
  port = sock.getsockname()[ 1 ]
  sock.close()
  return port


def PrettyPrintDict( value ):

  return json.dumps( value, sort_keys = True, indent = 2 ).replace(
        '\\n', '\n')


def BuildRequestData( test_filename = None,
                      filetype = None,
                      line_num = None,
                      column_num = None,
                      command_arguments = None,
                      completer_target = None ):
  test_path = PathToTestFile( test_filename ) if test_filename else ''

  contents = open( test_path ).read() if test_path else ''

  data = {
    'line_num': line_num,
    'column_num': column_num,
    'filepath': test_path,
    'file_data': {
      test_path: {
        'filetypes': [ filetype ],
        'contents': contents
      }
    }
  }

  if command_arguments:
    data[ 'command_arguments' ] = command_arguments
  if completer_target:
    data[ 'completer_target' ] = completer_target

  return data


def Main():
  print( 'Trying to start server...' )
  server = YcmdHandle.StartYcmdAndReturnHandle()
  server.WaitUntilReady()

  server.LoadExtraConfFile( PATH_TO_EXTRA_CONF )

  server.SendEventNotification( Event.FileReadyToParse,
                                test_filename = 'some_cpp.cpp',
                                filetype = 'cpp' )

  server.SendCodeCompletionRequest( test_filename = 'some_cpp.cpp',
                                    filetype = 'cpp',
                                    line_num = 25,
                                    column_num = 7 )

  print( 'Shutting down server...' )
  server.Shutdown()


if __name__ == "__main__":
  Main()

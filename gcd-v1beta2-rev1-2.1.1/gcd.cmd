@echo off
rem Copyright 2013 Google Inc. All Rights Reserved.
rem
rem Licensed under the Apache License, Version 2.0 (the "License");
rem you may not use this file except in compliance with the License.
rem You may obtain a copy of the License at
rem
rem     http://www.apache.org/licenses/LICENSE-2.0
rem
rem Unless required by applicable law or agreed to in writing, software
rem distributed under the License is distributed on an "AS IS" BASIS,
rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
rem See the License for the specific language governing permissions and
rem limitations under the License.
rem
rem Command-line tool for interacting with Google Cloud Datastore.

setlocal

set GCD_DIR=%~dp0
set GCD=%~f0
set DATASTORE_JAR=%GCD_DIR%\CloudDatastore.jar
set APPENGINE_TOOLS_JAR=%GCD_DIR%\.appengine\lib\appengine-tools-api.jar
set APPENGINE_API_STUBS_JAR=%GCD_DIR%\.appengine\lib\impl\appengine-api-stubs.jar

if NOT EXIST "%DATASTORE_JAR%" (
  echo %DATASTORE_JAR% not found
  exit /B 1
)

if NOT EXIST "%APPENGINE_TOOLS_JAR%" (
  echo %APPENGINE_TOOLS_JAR% not found
  exit /B 1
)

if NOT EXIST "%APPENGINE_API_STUBS_JAR%" (
  echo %APPENGINE_API_STUBS_JAR% not found
  exit /B 1
)

java -cp "%DATASTORE_JAR%";"%APPENGINE_TOOLS_JAR%";"%APPENGINE_API_STUBS_JAR%" ^
    com.google.apphosting.client.datastoreservice.tools.CloudDatastore "%GCD%" %* 

endlocal

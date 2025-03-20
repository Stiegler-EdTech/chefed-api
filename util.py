import os
import json

from enum import Enum

class LogLevel(Enum):
    Verbose = 1
    Info = 2
    Warning = 3
    Error = 4

def log(level:LogLevel, message):
    print(f"{level}: {message}")


def log_info(message):
    log(LogLevel.Info,message)    

def log_warning(message):
    log(LogLevel.Warning,message)    

def log_verbose(message):
    log(LogLevel.Verbose,message)    

def log_error(message):
    log(LogLevel.Error,message)    
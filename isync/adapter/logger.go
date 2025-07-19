package main

import (
	"fmt"
	"log"
	"os"
	"runtime"
	"strings"
	"time"
)

// LogLevel represents different logging levels
type LogLevel int

const (
	DEBUG LogLevel = iota
	INFO
	WARN
	ERROR
)

// String returns the string representation of the log level
func (l LogLevel) String() string {
	switch l {
	case DEBUG:
		return "DEBUG"
	case INFO:
		return "INFO"
	case WARN:
		return "WARN"
	case ERROR:
		return "ERROR"
	default:
		return "UNKNOWN"
	}
}

// Logger provides structured logging functionality
type Logger struct {
	level  LogLevel
	logger *log.Logger
}

// NewLogger creates a new logger with the specified level
func NewLogger(levelStr string) *Logger {
	var level LogLevel
	switch strings.ToLower(levelStr) {
	case "debug":
		level = DEBUG
	case "info":
		level = INFO
	case "warn":
		level = WARN
	case "error":
		level = ERROR
	default:
		level = INFO
	}

	return &Logger{
		level:  level,
		logger: log.New(os.Stdout, "", 0), // We'll handle our own formatting
	}
}

// Global logger instance
var logger *Logger

// InitLogger initializes the global logger
func InitLogger(level string) {
	logger = NewLogger(level)
}

// formatMessage formats a log message with timestamp, level, and caller info
func (l *Logger) formatMessage(level LogLevel, msg string, args ...interface{}) string {
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	
	// Get caller info
	_, file, line, _ := runtime.Caller(3) // Skip formatMessage, log method, and public method
	filename := file[strings.LastIndex(file, "/")+1:]
	
	// Format the base message
	formatted := fmt.Sprintf("[%s] %s %s:%d - %s", 
		timestamp, level.String(), filename, line, msg)
	
	// Add key-value pairs if provided
	if len(args) > 0 {
		if len(args)%2 != 0 {
			// Odd number of args, treat last one as a value with "data" key
			args = append([]interface{}{"data"}, args...)
		}
		
		var pairs []string
		for i := 0; i < len(args); i += 2 {
			key := fmt.Sprintf("%v", args[i])
			value := fmt.Sprintf("%v", args[i+1])
			pairs = append(pairs, fmt.Sprintf("%s=%s", key, value))
		}
		
		if len(pairs) > 0 {
			formatted += " | " + strings.Join(pairs, " ")
		}
	}
	
	return formatted
}

// log writes a message at the specified level
func (l *Logger) log(level LogLevel, msg string, args ...interface{}) {
	if level >= l.level {
		formatted := l.formatMessage(level, msg, args...)
		l.logger.Println(formatted)
	}
}

// Debug logs a debug message
func (l *Logger) Debug(msg string, args ...interface{}) {
	l.log(DEBUG, msg, args...)
}

// Info logs an info message
func (l *Logger) Info(msg string, args ...interface{}) {
	l.log(INFO, msg, args...)
}

// Warn logs a warning message
func (l *Logger) Warn(msg string, args ...interface{}) {
	l.log(WARN, msg, args...)
}

// Error logs an error message
func (l *Logger) Error(msg string, args ...interface{}) {
	l.log(ERROR, msg, args...)
}

// Fatal logs an error message and exits the program
func (l *Logger) Fatal(msg string, args ...interface{}) {
	l.log(ERROR, "FATAL: "+msg, args...)
	os.Exit(1)
}

// SetLevel changes the logging level
func (l *Logger) SetLevel(levelStr string) {
	switch strings.ToLower(levelStr) {
	case "debug":
		l.level = DEBUG
	case "info":
		l.level = INFO
	case "warn":
		l.level = WARN
	case "error":
		l.level = ERROR
	}
}

// Global convenience functions that use the global logger

// Debug logs a debug message using the global logger
func Debug(msg string, args ...interface{}) {
	if logger != nil {
		logger.Debug(msg, args...)
	}
}

// Info logs an info message using the global logger
func Info(msg string, args ...interface{}) {
	if logger != nil {
		logger.Info(msg, args...)
	}
}

// Warn logs a warning message using the global logger
func Warn(msg string, args ...interface{}) {
	if logger != nil {
		logger.Warn(msg, args...)
	}
}

// Error logs an error message using the global logger
func Error(msg string, args ...interface{}) {
	if logger != nil {
		logger.Error(msg, args...)
	}
}

// Fatal logs an error message and exits the program using the global logger
func Fatal(msg string, args ...interface{}) {
	if logger != nil {
		logger.Fatal(msg, args...)
	} else {
		fmt.Printf("FATAL: %s\n", msg)
		os.Exit(1)
	}
}
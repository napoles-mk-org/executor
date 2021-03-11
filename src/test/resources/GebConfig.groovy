// This is the Geb configuration file.
// See: http://www.gebish.org/manual/current/#configuration


import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.firefox.FirefoxDriver
import org.openqa.selenium.logging.LoggingPreferences
import org.openqa.selenium.remote.DesiredCapabilities
import java.util.logging.Level;
import org.openqa.selenium.logging.LogType;
import static java.util.logging.Level.ALL
import static org.openqa.selenium.logging.LogType.BROWSER
import static org.openqa.selenium.logging.LogType.DRIVER
import static org.openqa.selenium.logging.LogType.PERFORMANCE
import static org.openqa.selenium.remote.CapabilityType.LOGGING_PREFS


waiting {
  timeout = 2
}

environments {
  // run via “./gradlew chromeTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver
  chrome {
   DesiredCapabilities capabilities = DesiredCapabilities.chrome()
    ChromeOptions options = new ChromeOptions()
    options.setExperimentalOption("prefs", ["browser.custom_chrome_frame": false])
    options.addArguments('enable-logging')
    options.addArguments('v=1')
    options.addArguments('log-level=0')
    options.addArguments('log-file=detailed.log')
    capabilities.setCapability(ChromeOptions.CAPABILITY, options)
    LoggingPreferences logPrefs = new LoggingPreferences()
    logPrefs.enable(BROWSER, ALL)
    logPrefs.enable(DRIVER, ALL)
    logPrefs.enable(PERFORMANCE, ALL)
    capabilities.setCapability(LOGGING_PREFS, logPrefs)
    options.setCapability("goog:loggingPrefs", logPrefs);
    capabilities.setCapability(ChromeOptions.CAPABILITY, options)
    driver = { new ChromeDriver(options) } 
  }

  // run via “./gradlew chromeHeadlessTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver
  chromeHeadless {
    driver = {
      ChromeOptions o = new ChromeOptions()
      o.addArguments('headless')
      new ChromeDriver(o)
    }
  }
	
  // run via “./gradlew firefoxTest”
  // See: http://code.google.com/p/selenium/wiki/FirefoxDriver
  firefox {
    atCheckWaiting = 1
    driver = { new FirefoxDriver() }
  }
}

// To run the tests with all browsers just run “./gradlew test”
baseUrl = "http://gebish.org"

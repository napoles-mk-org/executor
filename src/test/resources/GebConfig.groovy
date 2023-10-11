// This is the Geb configuration file.
// See: http://www.gebish.org/manual/current/#configuration


import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.firefox.FirefoxDriver
import org.openqa.selenium.remote.DesiredCapabilities
import org.openqa.selenium.remote.CapabilityType
import org.openqa.selenium.remote.RemoteWebDriver

waiting {
  timeout = 20
}

environments {
  // run via “./gradlew chromeTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver
  chrome {
    driver = {
      ChromeOptions o = new ChromeOptions()
      o.addArguments('--no-sandbox');
      o.addArguments('--disable-dev-shm-usage');
      o.addArguments("--ignore-certificate-errors");
      DesiredCapabilities cap=DesiredCapabilities.chrome();
      cap.setCapability(ChromeOptions.CAPABILITY, o);
      cap.setCapability(CapabilityType.ACCEPT_SSL_CERTS, true);
      cap.setCapability(CapabilityType.ACCEPT_INSECURE_CERTS, true);
      new ChromeDriver(cap);
    }
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

  // run via “./gradlew browserstackTest
  browserstack{
    String USERNAME = "user";
    String AUTOMATE_KEY = "automatekey";
    String URL = "https://" + USERNAME + ":" + AUTOMATE_KEY + "@hub-cloud.browserstack.com/wd/hub";
    driver = {
      DesiredCapabilities caps = new DesiredCapabilities();
      caps.setCapability("os", "Windows");
      caps.setCapability("os_version", "10");
      caps.setCapability("browser", "Chrome");
      caps.setCapability("browser_version", "107.0");
      caps.setCapability("browserstack.local", "false");
      caps.setCapability("browserstack.debug", "true");
      caps.setCapability("browserstack.selenium_version", "3.6.0");
      new RemoteWebDriver(new URL(URL), caps);
    }
	}	
}

// To run the tests with all browsers just run “./gradlew test”
baseUrl = "http://gebish.org"

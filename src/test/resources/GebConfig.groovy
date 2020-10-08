// This is the Geb configuration file.
// See: http://www.gebish.org/manual/current/#configuration


import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.firefox.FirefoxDriver

waiting {
  timeout = 20
}

environments {
  // run via “./gradlew chromeTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver
  chrome {
    ChromeOptions o = new ChromeOptions()
    o.addArguments('--no-sandbox');
    o.addArguments('--disable-dev-shm-usage');
    driver = { new ChromeDriver(o) }
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

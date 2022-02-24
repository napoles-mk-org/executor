// This is the Geb configuration file.
// See: http://www.gebish.org/manual/current/#configuration

import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import io.netty.handler.codec.http.DefaultHttpHeaders;
import io.netty.handler.codec.http.HttpRequest;
import io.netty.handler.codec.http.HttpResponse;
import net.lightbody.bmp.BrowserMobProxy;
import net.lightbody.bmp.BrowserMobProxyServer;
import net.lightbody.bmp.client.ClientUtil;
import net.lightbody.bmp.filters.RequestFilter;
import net.lightbody.bmp.util.HttpMessageContents;
import net.lightbody.bmp.util.HttpMessageInfo;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.firefox.FirefoxOptions;

waiting {
  timeout = 20
}

environments {
  // run via “./gradlew chromeTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver
  chrome {

    /*
      BrowserMob Proxy allows you to manipulate HTTP requests and responses.
      This proxy help us to add ClinetID and Secret to bypass cloudflare 
      authentication on Steppingblocks tests.
    */
    BrowserMobProxyServer browserMobProxy = new BrowserMobProxyServer();
    browserMobProxy.setTrustAllServers(true);
    browserMobProxy.start(0);
    browserMobProxy.addRequestFilter(new RequestFilter() {
        @Override
        public HttpResponse filterRequest(HttpRequest httpRequest, HttpMessageContents httpMessageContents, HttpMessageInfo httpMessageInfo) {
            if(httpMessageInfo.getUrl().toString().contains("qa.crowdsegment.com/login")){
                DefaultHttpHeaders httpHeaders = new DefaultHttpHeaders();
                httpHeaders.add("CF-Access-Client-ID", "CLIENT_VALUE");
                httpHeaders.add("CF-Access-Client-Secret", "SECRET_VALUE");
                httpRequest.headers().add(httpHeaders);
            }
            else if(httpMessageInfo.getUrl().toString().contains("staging.crowdsegment.com/login")){
                DefaultHttpHeaders httpHeaders = new DefaultHttpHeaders();
                httpHeaders.add("CF-Access-Client-ID", "CLIENT_VALUE");
                httpHeaders.add("CF-Access-Client-Secret", "SECRET_VALUE");
                httpRequest.headers().add(httpHeaders);
            }
            return null;
        }
    });

    ChromeOptions o = new ChromeOptions()
    o.addArguments('--no-sandbox');
    o.addArguments('--disable-dev-shm-usage');

    // Set proxy on chrome options.
    o.setCapability(CapabilityType.PROXY, ClientUtil.createSeleniumProxy(browserMobProxy));
    o.addArguments("--ignore-certificate-errors");
    
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

     /*
      BrowserMob Proxy allows you to manipulate HTTP requests and responses.
      This proxy help us to add ClinetID and Secret to bypass cloudflare 
      authentication on Steppingblocks tests.
    */
    BrowserMobProxyServer browserMobProxy = new BrowserMobProxyServer();
    browserMobProxy.setTrustAllServers(true);
    browserMobProxy.start(0);
    browserMobProxy.addRequestFilter(new RequestFilter() {
        @Override
        public HttpResponse filterRequest(HttpRequest httpRequest, HttpMessageContents httpMessageContents, HttpMessageInfo httpMessageInfo) {
           if(httpMessageInfo.getUrl().toString().contains("qa.crowdsegment.com/login")){
                DefaultHttpHeaders httpHeaders = new DefaultHttpHeaders();
                httpHeaders.add("CF-Access-Client-ID", "CLIENT_VALUE");
                httpHeaders.add("CF-Access-Client-Secret", "SECRET_VALUE");
                httpRequest.headers().add(httpHeaders);
            }
            else if(httpMessageInfo.getUrl().toString().contains("staging.crowdsegment.com/login")){
                DefaultHttpHeaders httpHeaders = new DefaultHttpHeaders();
                httpHeaders.add("CF-Access-Client-ID", "CLIENT_VALUE");
                httpHeaders.add("CF-Access-Client-Secret", "SECRET_VALUE");
                httpRequest.headers().add(httpHeaders);
            }
            return null;
        }
    });

    atCheckWaiting = 1

    // Set proxy on firefox options.
    FirefoxOptions firefoxOptions = new FirefoxOptions();
    firefoxOptions.setCapability(CapabilityType.PROXY, ClientUtil.createSeleniumProxy(browserMobProxy));
    driver = { new FirefoxDriver(firefoxOptions) }
  }
}

// To run the tests with all browsers just run “./gradlew test”
baseUrl = "http://gebish.org"


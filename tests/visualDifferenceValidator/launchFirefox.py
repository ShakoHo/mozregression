import os
import time
import mozinfo
import pyscreenshot as ImageGrab
from threading import Thread
from mozrunner import Runner
from mozprofile import Profile
from imageAnalyzer import find_image_viewport
from windowController import WindowObject
from mozlog.structured import get_default_logger, get_proxy_logger


LOG = get_proxy_logger("windowController")


class FirefoxProfile(Profile):
    """
    Specialized Profile subclass for Firefox
    Some preferences may only apply to one or the other
    """

    preferences = {
        'app.update.enabled': False,
        # Don't restore the last open set of tabs
        # if the browser has crashed
        'browser.sessionstore.resume_from_crash': False,
        # Don't check for the default web browser during startup
        'browser.shell.checkDefaultBrowser': False,
        # Don't warn on exit when multiple tabs are open
        'browser.tabs.warnOnClose': False,
        # Don't warn when exiting the browser
        'browser.warnOnQuit': False,
        # Don't send Firefox health reports to the production
        # server
        'datareporting.healthreport.uploadEnabled': False,
        'datareporting.healthreport.documentServerURI':
            'http://%(server)s/healthreport/',
        # Don't show tab with privacy notice on every launch
        'datareporting.policy.dataSubmissionPolicyBypassNotification': True,
        # Don't report telemetry information
        'toolkit.telemetry.enabled': False,
        # Allow sideloading extensions
        'extensions.autoDisableScopes': 0,
        # added from Hasal config
        "browser.startup.homepage": "about:blank",
        "browser.startup.page": 0,
        "general.useragent.locale": "en-US",
        "intl.accept_languages": "en-US, en",
        "browser.sessionstore.restore_on_demand": False,
        "browser.eme.ui.enabled": False,
        "browser.urlbar.daysBeforeHidingSuggestionsPrompt": 0,
        "browser.urlbar.timesBeforeHidingSuggestionsHint": 0,
        "browser.startup.homepage_override.mstone": "ignore",
        "toolkit.startup.last_success": int(time.time())
    }


class FirefoxLauncher:

    def __init__(self, binary_path):
        self.binary = binary_path
        self._stopping = False
        self.env = dict(os.environ)

        # init gecko profiler
        self.env.update({
            'MOZ_PROFILER_STARTUP': '1',
            'MOZ_PROFILER_STARTUP_INTERVAL': str(1),
            'MOZ_PROFILER_STARTUP_ENTRIES': str(1000000)
        })


    def create_firefox_profile(self, profile=None, addons=(), preferences=None, clone=True):
        if profile:
            if not os.path.exists(profile):
                LOG.warning(
                    "Creating directory '%s' to put the profile in there"
                    % profile
                )
                os.makedirs(profile)
                # since the user gave an empty dir for the profile,
                # let's keep it on the disk in any case.
                clone = False
            if clone:
                # mozprofile makes some changes in the profile that can not
                # be undone. Let's clone the profile to not have side effect
                # on existing profile.
                # see https://bugzilla.mozilla.org/show_bug.cgi?id=999009
                profile = FirefoxProfile.clone(profile, addons=addons,
                                                  preferences=preferences)
            else:
                profile = FirefoxProfile(profile, addons=addons,
                                            preferences=preferences)
        elif len(addons):
            profile = FirefoxProfile(addons=addons,
                                        preferences=preferences)
        else:
            profile = FirefoxProfile(preferences=preferences)
        return profile

    def get_browser_viewport(self, x1=0, y1=0, x2=1024, y2=768):
        # capture screen
        img_obj = ImageGrab.grab((x1, y1, x2, y2))

        # analyze viewport
        current_viewport = find_image_viewport(img_obj)

        return current_viewport

    def is_browser_window_show_up(self):

        expected_viewport_width = 1000
        expected_viewport_height = 650

        for _ in range(30):
            # move window position
            window_obj = WindowObject(['Firefox.app', 'FirefoxNightly.app', 'FirefoxDeveloperEdition.app', 'Firefox Nightly'])
            window_obj.move_window_pos(0, 0, window_height=768, window_width=1024)

            # get viewport
            current_viewport = self.get_browser_viewport()

            if current_viewport["height"] >= expected_viewport_height or current_viewport["width"] >= expected_viewport_width:
                break

    def start(self, profile=None, addons=(), cmdargs=(), preferences=None):
        profile = self.create_firefox_profile(profile=profile, addons=addons, preferences=preferences)

        LOG.info("Launching %s" % self.binary)
        self.runner = Runner(binary=self.binary,
                             cmdargs=cmdargs,
                             profile=profile)

        def _on_exit():
            # if we are stopping the process do not log anything.
            if not self._stopping:
                # mozprocess (behind mozrunner) fire 'onFinish'
                # a bit early - let's ensure the process is finished.
                # we have to call wait() directly on the subprocess
                # instance of the ProcessHandler, else on windows
                # None is returned...
                # TODO: search that bug and fix that in mozprocess or
                # mozrunner. (likely mozproces)
                try:
                    exitcode = self.runner.process_handler.proc.wait()
                except Exception:
                    print
                    LOG.error(
                        "Error while waiting process, consider filing a bug.",
                        exc_info=True
                    )
                    return
                if exitcode != 0:
                    # first print a blank line, to be sure we don't
                    # write on an already printed line without EOL.
                    print
                    LOG.warning('Process exited with code %s' % exitcode)

        self.runner.process_args = {
            'processOutputLine': [get_default_logger("process").info],
            'onFinish': _on_exit,
        }
        self.runner.start()

    def stop(self):
        if mozinfo.os == "win":
            # for some reason, stopping the runner may hang on windows. For
            # example restart the browser in safe mode, it will hang for a
            # couple of minutes. As a workaround, we call that in a thread and
            # wait a bit for the completion. If the stop() can't complete we
            # forgot about that thread.
            thread = Thread(target=self.runner.stop)
            thread.daemon = True
            thread.start()
            thread.join(0.7)
        else:
            self.runner.stop()
        # release the runner since it holds a profile reference
        del self.runner


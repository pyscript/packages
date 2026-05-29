# ---------------------------------------------------------------------
# Section 2: Notification -- callbacks fire automatically when traits
# change. This is the feature that makes Traits especially nice for
# building reactive models and UIs.
# ---------------------------------------------------------------------

heading("Observing trait changes")
note(
    "Decorate a method with <code>@observe('trait_name')</code> and it "
    "is called every time that trait is set to a new value. The "
    "callback receives an event with <code>old</code> and "
    "<code>new</code> attributes."
)


class Thermostat(HasTraits):
    """A thermostat that logs every adjustment and clamps the setpoint."""

    setpoint_c = Range(low=5, high=30, value=20)
    mode = Enum("off", "heat", "cool")
    log = List(Str)

    @observe("setpoint_c")
    def _on_setpoint(self, event):
        self.log.append(
            f"setpoint: {event.old} -> {event.new} \u00b0C"
        )

    @observe("mode")
    def _on_mode(self, event):
        self.log.append(f"mode: {event.old!r} -> {event.new!r}")

    # Observe several traits at once with a comma-separated list.
    @observe("setpoint_c, mode")
    def _summarize(self, event):
        self.log.append(
            f"  (now: {self.mode} at {self.setpoint_c} \u00b0C)"
        )


t = Thermostat()
t.mode = "heat"
t.setpoint_c = 22
t.setpoint_c = 18
t.mode = "cool"

note("Event log produced by the observers:")
display(HTML("<pre>" + "\n".join(t.log) + "</pre>"), append=True)


# Observers can also be attached dynamically, from outside the class.
heading("Dynamic observers")
note(
    "Use <code>obj.observe(handler, 'trait_name')</code> to subscribe "
    "after the fact -- handy for wiring up loosely coupled components."
)

alerts = []

def warn_if_hot(event):
    if event.new >= 25:
        alerts.append(f"\u26a0 high setpoint requested: {event.new} \u00b0C")

t.observe(warn_if_hot, "setpoint_c")
t.setpoint_c = 24   # no alert
t.setpoint_c = 27   # triggers alert
t.setpoint_c = 30   # triggers alert

display(HTML("<pre>" + "\n".join(alerts) + "</pre>"), append=True)

/**
 * A wizard widget that actually works with minimal configuration. (per jQuery's design philosophy)
 *
 * @name	jWizard jQuery UI Widget
 * @author	Dominic Barnes
 *
 * @requires jQuery
 * @requires jQuery UI (Widget Factory; ProgressBar optional; Button optional)
 */
(function ($) {
	/**
	 * @class The jWizard object will be fed into $.widget()
	 */
	$.widget("db.jWizard", {
		/**
		 * @private
		 * @property int _stepIndex Represents the index of the current active/visible step
		 */
		_stepIndex: 0,

		/**
		 * @private
		 * @property int _stepCount Represents the `functional` number of steps
		 */
		_stepCount: 0,

		/**
		 * @private
		 * @property int _actualCount Represents the `actual` number of steps
		 */
		_actualCount: 0,

		/**
		 * @description Initializes jWizard
		 * @return void
		 */
		_create: function () {
			this._buildSteps();
			this._buildTitle();

			if (this.options.menuEnable) {
				this._buildMenu();
			}

			this._buildButtons();

			if (this.options.counter.enable) {
				this._buildCounter();
			}

			this.element.addClass("ui-widget jw-widget");

			this._hoverable(this.element.find(".ui-state-default"));

			this._changeStep(this._stepIndex, true);
		},

		/**
		 * @private
		 * @description Additional processing before destroying the widget.
		 *    Will eventually be used to restore everything to it's pre-widget state.
		 * @return void
		 */
		destroy: function () {
			this._destroySteps();
			this._destroyTitle();

			if (this.options.menuEnable) {
				this._destroyMenu();
			}

			this._destroyButtons();

			if (this.options.counter.enable) {
				this._destroyCounter();
			}

			this.element.removeClass("ui-widget jw-widget");

			this._super();
		},

		/**
		 * @public
		 * @description Disables the wizard (mainly the buttons)
		 */
		disable: function () {
			this.element.addClass("ui-state-disabled").find("button").attr("disabled", "disabled");
		},

		/**
		 * @public
		 * @description Disables the wizard (mainly the buttons)
		 */
		enable: function () {
			this.element.removeClass("ui-state-disabled").find("button").removeAttr("disabled");
		},

		option: function (key, val) {
			this._superApply(arguments);

			if (typeof key === "string" && typeof val !== "undefined") {
				var keys = key.split(".");

				switch (keys[0]) {
				case "buttons":
					switch (keys[1]) {
					case "jqueryui":
						if (keys[2] === "enable") {
							if (val) {
								this.find(".jw-buttons > button").button("destroy");
							} else {
								this._destroyButtons();
								this._buildButtons();
							}
							break;
						}
						break;

					case "cancelHide":
						this.element.find(".jw-button-cancel").toggleClass("ui-helper-hidden", !!val);
						break;

					case "cancelType":
						this.element.find(".jw-button-cancel").attr("type", val);
						break;

					case "finishType":
						this.element.find(".jw-button-finish").attr("type", val);
						break;

					case "cancelText":
						this.element.find(".jw-button-cancel").text(val);
						break;

					case "previousText":
						this.element.find(".jw-button-previous").text(val);
						break;

					case "nextText":
						this.element.find(".jw-button-next").text(val);
						break;

					case "finishText":
						this.element.find(".jw-button-finish").text(val);
						break;
					}
					break;

				case "counter":
					switch (keys[1]) {
					case "enable":
						if (value) {
							this._buildCounter();
							this._updateCounter();
						} else {
							this._destroyCounter();
						}
						break;
					case "type":
					case "progressbar":
					case "location":
						if (this.options.counter.enable) {
							this._destroyCounter();
							this._buildCounter();
							this._updateCounter();
						}
						break;
					case "startCount":
					case "startHide":
					case "finishCount":
					case "finishHide":
					case "appendText":
					case "orientText":
						if (this.options.counter.enable) {
							this._updateCounter();
						}
						break;
					}
					break;
				}
			}
		},

		/**
		 * @private
		 * @description Can set options within the widget programmatically
		 * @return void
		 */
		_setOption: function (key, val) {
			this._superApply(arguments);

			switch (key) {
			case "titleHide":
				this.element.find(".jw-header").toggleClass("ui-helper-hidden", !!val);
				break;

			case "menuEnable":
				if (val) {
					this._buildMenu();
					this._updateMenu();
				} else {
					this._destroyMenu();
				}
				break;

			case "counter":
				this._destroyCounter();
				this._buildCounter();
				this._updateCounter();
				break;
			}
		},

		/**
		 * @description Jumps to the first step in the wizard's step collection
		 * @return void
		 */
		firstStep: function () {
			this.changeStep(0, "first");
		},

		/**
		 * @description Jumps to the last step in the wizard's step collection
		 * @return void
		 */
		lastStep: function () {
			this.changeStep(this._stepCount - 1, "last");
		},

		/**
		 * @description Jumps to the next step in the wizard's step collection
		 * @return void
		 */
		nextStep: function () {
			var options = {
				wizard: this.element,
				currentStepIndex: this._stepIndex,
				nextStepIndex: this._stepIndex + 1,
				delta: 1
			};

			if (this._trigger("next", null, options) !== false) {
				this.changeStep(this._stepIndex + 1, "next");
			}
		},

		/**
		 * @description Jumps to the previous step in the wizard's step collection
		 * @return void
		 */
		previousStep: function () {
			var options = {
				wizard: this.element,
				currentStepIndex: this._stepIndex,
				nextStepIndex: this._stepIndex - 1,
				delta: -1
			};

			if (this._trigger("previous", null, options) !== false) {
				this.changeStep(this._stepIndex - 1, "previous");
			}
		},

		/**
		 * @description Goes to an arbitrary `step` in the collection based on input
		 * @return void
		 */
		changeStep: function (nextStep, type) {
			type = type || "manual";
			nextStep = typeof nextStep === "number" ? nextStep : $(nextStep).index();
			var options = {
				wizard: this.element,
				currentStepIndex: this._stepIndex,
				nextStepIndex: nextStep,
				delta: nextStep - this._stepIndex,
				type: type
			};

			if (this._trigger("changestep", null, options) !== false) {
				this._changeStep(nextStep);
			}
		},

		/**
		 * @private
		 * @description Internal wrapper for performing animations
		 * @return void
		 */
		_effect: function ($element, action, subset, type, callback) {
			var wizard = this,
				opt = this.options.effects[action][subset];

			type = type || "effect";

			if (!$element.length || !$element.hasClass("jw-animated")) {
				$element[type]();

				if (callback) {
					callback.call(this);
				}

				return false;
			}

			opt.callback = callback || $.noop;

			$element[type](opt.type, opt.options, opt.duration, opt.callback);
		},

		_updateNavigation: function (firstStep) {
			this._updateButtons();
			if (this.options.menuEnable) {
				this._updateMenu(firstStep);
			}
			if (this.options.counter.enable) {
				this._updateCounter(firstStep);
			}
		},

		/**
		 * @private
		 * @description Generates the header/title
		 * @return void
		 */
		_buildTitle: function () {
			this.element.prepend($("<div />", {
				"class": "jw-header ui-widget-header ui-corner-top" + (this.options.titleHide ? " ui-helper-hidden" : ""),
				html: '<h2 class="jw-title' + ((this.options.effects.enable || this.options.effects.title.enable) ? " jw-animated" : "") + '" />'
			}));
		},

		/**
		 * @private
		 * @description Updates the title
		 * @return void
		 */
		_updateTitle: function (firstStep) {
			var wizard = this,
				$title = this.element.find(".jw-title"),
				$currentStep = this.element.find(".jw-step:eq(" + this._stepIndex + ")");

			if (!firstStep) {
				this._effect($title, "title", "hide", "hide", function () {
					$title.text($currentStep.attr("title") || $currentStep.data("title"));
					wizard._effect($title, "title", "show", "show");
				});
			} else {
				$title.text($currentStep.attr("title"));
			}
		},

		/**
		 * @private
		 * @description Destroys the title element (used in `destroy()`)
		 * @return void
		 */
		_destroyTitle: function () {
			this.element.children(".jw-header").remove();
		},

		/**
		 * @private
		 * @description Initializes the step collection.
		 *    Any direct children <div> (with a title attr) or <fieldset> (with a <legend>) are considered steps, and there should be no other sibling elements.
		 *    All steps without a specified `id` attribute are assigned one based on their index in the collection.
		 *    Lastly, a <div> is wrapped around all the steps to isolate them from the rest of the widget.
		 * @return void
		 */
		_buildSteps: function () {
			var $steps = this.element.children("div, fieldset");

			this._stepCount = $steps.length;

			$steps.addClass("jw-step").each(function (x) {
				var $step = $(this);

				if (this.tagName.toLowerCase() === "fieldset") {
					$step.attr("title", $step.find("legend").text());
				}
			});

			if (this.options.effects.enable || this.options.effects.step.enable) {
				$steps.addClass("jw-animated");
			}

			$steps.hide().wrapAll($("<div />", {
				"class": "jw-content ui-widget-content ui-helper-clearfix",
				html: '<div class="jw-steps-wrap" />'
			})).eq(this._stepIndex).show();
		},

		/**
		 * @private
		 * @description Destroys the step wrappers and restores the steps to their original state (used in `destroy()`)
		 * @return void
		 */
		_destroySteps: function () {
			// Unwrap 2x: .jw-steps-wrap + .jw-content
			this.element.find(".jw-step").show().unwrap().unwrap()
				.unbind("show hide").removeClass("jw-step");
		},

		/**
		 * @private
		 * @description Changes the "active" step.
		 * @param number|jQuery nextStep Either an index or a jQuery object/element
		 * @param bool isInit Behavior needs to change if this is called during _init (as opposed to manually through the global setter)
		 * @return void
		 */
		_changeStep: function (nextStep, firstStep) {
			var wizard = this,
				$steps = this.element.find(".jw-step"),
				$currentStep = $steps.eq(this._stepIndex);

			if (typeof nextStep === "number") {
				if (nextStep < 0 || nextStep > ($steps.length - 1)) {
					alert("Index " + nextStep + " Out of Range");
					return false;
				}

				nextStep = $steps.eq(nextStep);
			} else if (typeof nextStep === "object") {
				if (!nextStep.is($steps.selector)) {
					alert("Supplied Element is NOT one of the Wizard Steps");
					return false;
				}
			}

			if (!firstStep) {
				this._disableButtons();
				this._stepIndex = $steps.index(nextStep);
				this._updateTitle(firstStep);

				this._effect($currentStep, "step", "hide", "hide", function () {
					wizard._effect(nextStep, "step", "show", "show", function () {
						wizard._enableButtons();
						wizard._updateNavigation(firstStep);
					});
				});
			} else {
				this._stepIndex = $steps.index(nextStep);
				this._updateTitle(firstStep);
				this._updateNavigation(firstStep);
			}
		},

		/**
		 * @private
		 * @description Initializes the menu
		 *    Builds the menu based on the collection of steps
		 *    Assigns a class to the main <div> to indicate to CSS that there is a menu
		 *    Binds a click event to each of the <a> that will change the step accordingly when clicked
		 * @return void
		 */
		_buildMenu: function () {
			var list = [], $menu, $anchors;

			this.element.addClass("jw-hasmenu");
			this.element.find(".jw-step").each(function (x) {
				list.push($("<li />", {
					"class": "ui-corner-all " + (x === 0 ? "jw-current ui-state-highlight" : "jw-inactive ui-state-disabled"),
					html: $("<a />", {
						step: x,
						text: $(this).attr("title")
					})
				})[0]);
			});

			$menu = $("<div />", {
				"class": "jw-menu-wrap",
				html: $("<div />", {
					"class": "jw-menu",
					html: $("<ol />", { html: $(list) })
				})
			});

			this.element.find(".jw-content").prepend($menu);

			if (this.options.effects.enable || this.options.effects.menu.enable) {
				$menu.find("li").addClass("jw-animated");
			}

			$menu.find("a").click($.proxy(function (event) {
				var $target = $(event.target),
					nextStep = parseInt($target.attr("step"), 10);

				if ($target.parent().hasClass("jw-active")) {
					this.changeStep(nextStep, nextStep <= this._stepIndex ? "previous" : "next");
				}
			}, this));
		},

		/**
		 * @private
		 * @description Removes the 'jw-hasmenu' class and pulls the menu out of the DOM entirely
		 * @return void
		 */
		_destroyMenu: function () {
			this.element.removeClass("jw-hasmenu").find(".jw-menu-wrap").remove();
		},

		/**
		 * @private
		 * @description Updates the menu at the end of each call to _changeStep()
		 *    Each <a> is looped over, along with the parent <li>
		 *    Status (jw-current, jw-active, jw-inactive) set depending on progress through wizard
		 * @see this._changeStep()
		 * @return void
		 */
		_updateMenu: function (firstStep) {
			var wizard = this,
				currentStep = this._stepIndex,
				$menu = this.element.find(".jw-menu");

			if (!firstStep) {
				this._effect($menu.find("li:eq(" + currentStep + ")"), "menu", "change");
			}

			$menu.find("a").each(function (x) {
				var $a = $(this),
					$li = $a.parent(),
					iStep = parseInt($a.attr("step"), 10),
					sClass = "";

				if (iStep < currentStep) {
					sClass += "jw-active ui-state-default";
				} else if (iStep === currentStep) {
					sClass += "jw-current ui-state-highlight";
				} else if (iStep > currentStep) {
					sClass += "jw-inactive ui-state-disabled";
					$a.removeAttr("href");
				}

				$li.removeClass("jw-active jw-current jw-inactive ui-state-default ui-state-highlight ui-state-disabled").addClass(sClass);
			});
		},

		/**
		 * @private
		 * @description Initializes the step counter.
		 *    A new <span> is created and used as the main element
		 * @return void
		 */
		_buildCounter: function () {
			var $counter = $("<span />", { "class": "jw-counter ui-widget-content ui-corner-all jw-" + this.options.counter.orientText });

			if (this.options.counter.location === "header") {
				this.element.find(".jw-header").prepend($counter);
			} else if (this.options.counter.location === "footer") {
				this.element.find(".jw-footer").prepend($counter);
			}

			if (!this.options.counter.startCount) {
				this._stepCount--;
			}
			if (!this.options.counter.finishCount) {
				this._stepCount--;
			}

			if (this.options.effects.enable || this.options.effects.counter.enable) {
				$counter.addClass("jw-animated");
			}

			if (this.options.counter.progressbar) {
				$counter
					.html('<span class="jw-counter-text" /> <span class="jw-counter-progressbar" />')
					.find(".jw-counter-progressbar").progressbar();
			}
		},

		/**
		 * @private
		 * @description This is run at the end of every call to this._changeStep()
		 * @return void
		 * @see this._changeStep()
		 */
		_updateCounter: function (firstStep) {
			var $counter = this.element.find(".jw-counter"),
				counterOptions = this.options.counter,
				counterText = "",
				actualIndex = this._stepIndex,
				actualCount = this._stepCount,
				percentage = 0;

			if (!counterOptions.startCount) {
				actualIndex--;
				actualCount--;
			}

			if (!firstStep) {
				this._effect($counter, "counter", "change");
			}

			percentage = Math.round((actualIndex / actualCount) * 100);

			if (counterOptions.type === "percentage") {
				counterText = ((percentage <= 100) ? percentage : 100) + "%";
			} else if (counterOptions.type === "count") {
				if (actualIndex < 0) {
					counterText = 0;
				} else if (actualIndex > actualCount) {
					counterText = actualCount;
				} else {
					counterText = actualIndex;
				}

				counterText += " of " + actualCount;
			} else {
				counterText = "N/A";
			}

			if (counterOptions.appendText) {
				counterText += " " + counterOptions.appendText;
			}

			if (counterOptions.progressbar) {
				this.element.find(".jw-counter-progressbar").progressbar("option", "value", percentage);
				this.element.find(".jw-counter-text").text(counterText);
			} else {
				$counter.text(counterText);
			}

			if ((counterOptions.startHide && this._stepIndex === 0) || (counterOptions.finishHide && this._stepIndex === (this._actualCount - 1))) {
				$counter.hide();
			} else {
				$counter.show();
			}
		},

		/**
		 * @private
		 * @description Removes the counter DOM elements, resets _stepCount
		 * @return void
		 */
		_destroyCounter: function () {
			this.element.find(".jw-counter").remove();
		},

		/**
		 * @private
		 * @description This generates the <button> elements for the main navigation and binds `click` handlers to each of them
		 * @see this._changeStep()
		 */
		_buildButtons: function () {
			var self = this,
				options = this.options.buttons,
				$footer = $("<div />", { "class": "jw-footer ui-widget-header ui-corner-bottom" }),
				$cancel = $('<button type="' + options.cancelType + '" class="ui-state-default ui-corner-all jw-button-cancel ui-priority-secondary' + (options.cancelHide ? " ui-helper-hidden" : "") + '">' + options.cancelText + '</button>'),
				$previous = $('<button type="button" class="ui-state-default ui-corner-all jw-button-previous">' + options.previousText + '</button>'),
				$next = $('<button type="button" class="ui-state-default ui-corner-all jw-button-next">' + options.nextText + '</button>'),
				$finish = $('<button type="' + options.finishType + '" class="ui-state-default ui-corner-all jw-button-finish ui-state-highlight">' + options.finishText + '</button>');
			
			var count = 0;
			$cancel.click(function (event) {
				window.location.replace( "home.html" );
			});
			$previous.click(function (event) {
				var advanced = $(":input[name=advanced]").val();
				if((advanced == "false") && (count == 3)) { 
					self.previousStep();
					count = count - 2; 
				}
				else {
					self.previousStep();
					count--;
				}
			});
			$next.click(function (event) {
				var errorcount = 0;
				var advanced = $(":input[name=advanced]").val(); //determine if in advanced mode or standard mode
				
				if(count == 0) { 
					self.nextStep(); 
					count++;
				}
				else if(count == 1) {
					$(".reminder").remove();
					var sizeInput = jWizard.size;
					var floorInput = $("*[name='idf[number_of_floors]']").first();
					errorcount = validate(floorInput, floorInput.val(), "number", 1, 200, errorcount, true);
					errorcount = validate(sizeInput, $(":input[name=size]").val(), "number", 400, "", errorcount, true);
					if(advanced == "true") {
						var widthInput = $("*[name='idf[width1]']").first();
						var lengthInput = $("*[name='idf[length1]']").first();
						errorcount = validate(widthInput, widthInput.val(), "number", 20, "", errorcount, false);
						errorcount = validate(lengthInput, lengthInput.val(), "number", 20, "", errorcount, false);
					}
					else {}
					if(errorcount == 0) {
						self.nextStep();
						if(advanced == "true") { count++; }
						else { count = count + 2; }
					}
					else {
						$("#step2").before('<div class="important reminder">*Please enter the appropriate information in the highlighted fields.</div>');
					}
				}
				else if(count == 2){
					$(".reminder").remove();
					var timestepInput = $("*[name='idf[timestep]']").first();
					errorcount = validate(timestepInput, timestepInput.val(), "number", 0, "", errorcount, true);
					var runnumberInput = $("*[name='idf[run_number]']").first();
					errorcount = validate(runnumberInput, runnumberInput.val(), "number", 0, "", errorcount, true);
					var floorheightInput = $("*[name='idf[floor_height]']").first();
					errorcount = validate(floorheightInput, floorheightInput.val(), "number", 0, "", errorcount, true);
					var orientationInput = $("*[name='idf[orientation]']").first();
					errorcount = validate(orientationInput, orientationInput.val(), "number", 0, 360, errorcount, true);
					
					var southWwrInput = $("*[name='idf[south_wwr]']").first();
					errorcount = validate(southWwrInput, southWwrInput.val(), "number", 0, 1, errorcount, true);
					var eastWwrInput = $("*[name='idf[east_wwr]']").first();
					errorcount = validate(eastWwrInput, eastWwrInput.val(), "number", 0, 1, errorcount, true);
					var northWwrInput = $("*[name='idf[north_wwr]']").first();
					errorcount = validate(northWwrInput, northWwrInput.val(), "number", 0, 1, errorcount, true);
					var westWwrInput = $("*[name='idf[west_wwr]']").first();
					errorcount = validate(westWwrInput, westWwrInput.val(), "number", 0, 1, errorcount, true);
					var heatingEfficiencyInput = $("*[name='idf[heating_efficiency]']").first();
					errorcount = validate(heatingEfficiencyInput, heatingEfficiencyInput.val(), "number", 0, 1, errorcount, true);						
					var coolingCopInput = $("*[name='idf[cooling_cop]']").first();
					errorcount = validate(coolingCopInput, coolingCopInput.val(), "number", 0, "", errorcount, true);
					var fanEfficiencyInput = $("*[name='idf[fan_efficiency]']").first();
					errorcount = validate(fanEfficiencyInput, fanEfficiencyInput.val(), "number", 0, 1, errorcount, true);
					var fanStaticPressureInput = $("*[name='idf[fan_static_pressure]']").first();
					errorcount = validate(fanStaticPressureInput, fanStaticPressureInput.val(), "number", 0, "", errorcount, true);
					var elecPlugIntesityInput = $("*[name='idf[elec_plug_intensity]']").first();
					errorcount = validate(elecPlugIntesityInput, elecPlugIntesityInput.val(), "number", 0, "", errorcount, true);
					var intLightingIntensityInput = $("*[name='idf[int_lighting_intensity]']").first();
					errorcount = validate(intLightingIntensityInput, intLightingIntensityInput.val(), "number", 0, "", errorcount, true);
					var extLightingIntensityInput = $("*[name='idf[ext_lighting_intensity]']").first();
					errorcount = validate(extLightingIntensityInput, extLightingIntensityInput.val(), "number", 0, "", errorcount, true);
					var peopleDensityInput = $("*[name='idf[people_density]']").first();
					errorcount = validate(peopleDensityInput, peopleDensityInput.val(), "number", 0, "", errorcount, true);
					var infiltrationPerExtSurAreaInput = $("*[name='idf[infiltration_per_ext_sur_area]']").first();
					errorcount = validate(infiltrationPerExtSurAreaInput, infiltrationPerExtSurAreaInput.val(), "number", 0, "", errorcount, true);
					var oaVentPerPersonInput = $("*[name='idf[oa_vent_per_person]']").first();
					errorcount = validate(oaVentPerPersonInput, oaVentPerPersonInput.val(), "number", 0, "", errorcount, true);
					var oaVentPerAreaInput = $("*[name='idf[oa_vent_per_area]']").first();
					errorcount = validate(oaVentPerAreaInput, oaVentPerAreaInput.val(), "number", 0, "", errorcount, true);
					var lengthTwoInput = $("*[name='idf[length2]']").first();
					errorcount = validate(lengthTwoInput, lengthTwoInput.val(), "number", 0, "", errorcount, true);
					var widthTwoInput = $("*[name='idf[width2]']").first();
					errorcount = validate(widthTwoInput, widthTwoInput.val(), "number", 0, "", errorcount, true);
					var endOneInput = $("*[name='idf[end1]']").first();
					errorcount = validate(endOneInput, endOneInput.val(), "number", 0, "", errorcount, true);
					var endTwoInput = $("*[name='idf[end2]']").first();
					errorcount = validate(endTwoInput, endTwoInput.val(), "number", 0, "", errorcount, true);
					var offsetOneInput = $("*[name='idf[offset1]']").first();
					errorcount = validate(offsetOneInput, offsetOneInput.val(), "number", 0, "", errorcount, true);
					var offsetTwoInput = $("*[name='idf[offset2]']").first();
					errorcount = validate(offsetTwoInput, offsetTwoInput.val(), "number", 0, "", errorcount, true);
					var offsetThreeInput = $("*[name='idf[offset3]']").first();
					errorcount = validate(offsetThreeInput, offsetThreeInput.val(), "number", 0, "", errorcount, true);
					var coolingSetbackInput = $("*[name='idf[cooling_setback]']").first();
					errorcount = validate(coolingSetbackInput, coolingSetbackInput.val(), "number", 0, "", errorcount, true);
					var heatingSetbackInput = $("*[name='idf[heating_setback]']").first();
					errorcount = validate(heatingSetbackInput, heatingSetbackInput.val(), "number", 0, "", errorcount, true);
					var coolingSetpointInput = $("*[name='idf[cooling_setpoint]']").first();
					errorcount = validate(coolingSetpointInput, coolingSetpointInput.val(), "number", 0, "", errorcount, true);
					var heatingSetpointInput = $("*[name='idf[heating_setpoint]']").first();
					errorcount = validate(heatingSetpointInput, heatingSetpointInput.val(), "number", 0, "", errorcount, true);
					
					if(errorcount == 0) {
						self.nextStep();
						count++;
					}
					else {
						$("#step3").before('<div class="important reminder">*Please enter the appropriate information in the highlighted fields.</div>');
						timestepInput.focus();
					}
				}
				else if(count == 3) {
					$(".reminder").remove();
					if($(":input[name=location]").val() == "none") {  $("#step4").before('<div class="important reminder">*Please select a location.</div>'); }
					else { 
						self.nextStep();
						count++;
					}
				}
				else if(count == 4) {
					$(".reminder").remove();

					var eJan = $("*[name='energyUsage[0]']");
					var eFeb = $("*[name='energyUsage[1]']");
					var eMar = $("*[name='energyUsage[2]']");
					var eApr = $("*[name='energyUsage[3]']");
					var eMay = $("*[name='energyUsage[4]']");
					var eJun = $("*[name='energyUsage[5]']");
					var eJul = $("*[name='energyUsage[6]']");
					var eAug = $("*[name='energyUsage[7]']");
					var eSep = $("*[name='energyUsage[8]']");
					var eOct = $("*[name='energyUsage[9]']");
					var eNov = $("*[name='energyUsage[10]']");
					var eDec = $("*[name='energyUsage[11]']");
					
					var gJan = $("*[name='gasUsage[0]']");
					var gFeb = $("*[name='gasUsage[1]']");
					var gMar = $("*[name='gasUsage[2]']");
					var gApr = $("*[name='gasUsage[3]']");
					var gMay = $("*[name='gasUsage[4]']");
					var gJun = $("*[name='gasUsage[5]']");
					var gJul = $("*[name='gasUsage[6]']");
					var gAug = $("*[name='gasUsage[7]']");
					var gSep = $("*[name='gasUsage[8]']");
					var gOct = $("*[name='gasUsage[9]']");
					var gNov = $("*[name='gasUsage[10]']");
					var gDec = $("*[name='gasUsage[11]']");
					
					var eInput = new Array(eJan, eFeb, eMar, eApr, eMay, eJun, eJul, eAug, eSep, eOct, eNov, eDec);
					var gInput = new Array(gJan, gFeb, gMar, gApr, gMay, gJun, gJul, gAug, gSep, gOct, gNov, gDec);
					
					var eFile = jWizard.energyFile.value;
					var gFile = jWizard.gasFile.value;
					var tFile = jWizard.tempFile.value;
					
					var eBlanks = checkForBlanks(eInput);
					var gBlanks = checkForBlanks(gInput);
					
					
					if(eFile == "" && eBlanks == true) {
						$("#electricity").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table.</div>');
						$("#electricity").before('<span class="important reminder">*   </span>');
						validateMonthlyInput(eInput);
						if(gFile == "" && gBlanks == true) {
							$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table.</div>');
							$("#gas").before('<span class="important reminder">*   </span>');
							validateMonthlyInput(gInput);
							if(tFile == "") { 
								$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(tFile.indexOf(".csv") > 0) {
								$(".reminder").remove();
								self.nextStep();
								count++;
							}
						}
						//else if(gFile != "" && gBlanks == false) {
							//code for forcing user to upload a file OR fill in the table
						//}
						else if(gFile != "" && !(gFile.indexOf(".csv") > 0)) {
							$("#gas").before('<div class="important reminder">*Please upload a .csv file.</div>');
							$("#gas").before('<span class="important reminder">*   </span>');
							if(tFile == "") { 
								$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
						}
						else if(gBlanks == false) {
							$(".reminder").remove();
							errorcount = validateMonthlyInput(gInput);
							if(errorcount == 0) {
								if(tFile == "") { 
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(tFile.indexOf(".csv") > 0) {
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
							}
							else {
								$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table with the appropriate information.</div>');
								$("#gas").before('<span class="important reminder">*   </span>');
								if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							}
						}
						else if(gFile != "" && (gFile.indexOf(".csv") > 0)) {
							if(tFile == "") { 
								$(".reminder").remove();
								self.nextStep();
								count++;
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(tFile.indexOf(".csv") > 0) {
								$(".reminder").remove();
								self.nextStep();
								count++;
							}
						}
					}
					//else if(eFile != "" && eBlanks == false) {  code to handle forcing the user to upload a file OR fill in the table}
					else if(eFile != "" && !(eFile.indexOf(".csv") > 0)) {
						$("#electricity").before('<div class="important reminder">*Please upload a .csv file.</div>');
						$("#electricity").before('<span class="important reminder">*   </span>');
						if(gFile == "" && gBlanks == true) {
							$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table.</div>');
							$("#gas").before('<span class="important reminder">*   </span>');
							validateMonthlyInput(gInput);
							if(tFile == "") { 
								$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
						}
						//else if(gFile != "" && gBlanks == false) {
							//code for forcing user to upload a file OR fill in the table
						//}
						else if(gFile != "" && !(gFile.indexOf(".csv") > 0)) {
							$("#gas").before('<div class="important reminder">*Please upload a .csv file.</div>');
							$("#gas").before('<span class="important reminder">*   </span>');
							if(tFile == "") { 
								$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
						}
						else if(gBlanks == false) {
							//$(".reminder").remove();
							errorcount = validateMonthlyInput(gInput);
							if(errorcount == 0) {
								//self.nextStep();
								//count++;
								if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							}
							else {
								$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table with the appropriate information.</div>');
								$("#gas").before('<span class="important reminder">*   </span>');
								if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							}
						}
						else if(gFile != "" && (gFile.indexOf(".csv") > 0)) {
							//$(".reminder").remove();
							//self.nextStep();
							//count++;
							if(tFile == "") { 
								$("#temp").before('<div class="important reminder">*Please select a file for upload.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
						}
					}
					else if(eBlanks == false) {
						var errorcountElectricity = validateMonthlyInput(eInput);
						if(errorcountElectricity == 0) {}
						else {
							$("#electricity").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table with the appropriate information.</div>');
							$("#electricity").before('<span class="important reminder">*   </span>');
						}
						
						if(gFile == "" && gBlanks == true) {
							errorcountGas = validateMonthlyInput(gInput);
							if(errorcountGas == 0 && errorcountElectricity == 0) {
								if(tFile == "") { 
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(tFile.indexOf(".csv") > 0) {
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
							}
							else {
								$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table.</div>');
								$("#gas").before('<span class="important reminder">*   </span>');
								if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							}
						}
						//else if(gFile != "" && gBlanks == false) {
							//code for forcing user to upload a file OR fill in the table
						//}
						else if(gFile != "" && !(gFile.indexOf(".csv") > 0)) {
							$("#gas").before('<div class="important reminder">*Please upload a .csv file.</div>');
							$("#gas").before('<span class="important reminder">*   </span>');
							if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
							}
						}
						else if(gBlanks == false) {
							$(".reminder").remove();
							errorcount = validateMonthlyInput(gInput);
							if(errorcount == 0 && errorcountElectricity == 0) {
								if(tFile == "") { 
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(tFile.indexOf(".csv") > 0) {
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
							}
							else {
								$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table with the appropriate information.</div>');
								$("#gas").before('<span class="important reminder">*   </span>');
								if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							}
						}
						else if(gFile != "" && (gFile.indexOf(".csv") > 0)) {
							if(tFile == "") { 
								$(".reminder").remove();
								self.nextStep();
								count++;
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(tFile.indexOf(".csv") > 0) {
								$(".reminder").remove();
								self.nextStep();
								count++;
							}
						}
					}
					else if(eFile != "" && (eFile.indexOf(".csv") > 0)) {
						if(gFile == "" && gBlanks == true) {
							errorcount = validateMonthlyInput(gInput);
							if(errorcount == 12) {
								if(tFile == "") { 
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(tFile.indexOf(".csv") > 0) {
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
							}
							else {
								$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table.</div>');
								$("#gas").before('<span class="important reminder">*   </span>');
								if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							}
						}
						//else if(gFile != "" && gBlanks == false) {
							//code for forcing user to upload a file OR fill in the table
						//}
						else if(gFile != "" && !(gFile.indexOf(".csv") > 0)) {
							$("#gas").before('<div class="important reminder">*Please upload a .csv file.</div>');
							$("#gas").before('<span class="important reminder">*   </span>');
							if(tFile == "") { 
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
						}
						else if(gBlanks == false) {
							errorcount = validateMonthlyInput(gInput);
							if(errorcount == 0) {
								if(tFile == "") { 
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(tFile.indexOf(".csv") > 0) {
									$(".reminder").remove();
									self.nextStep();
									count++;
								}
							}
							else {
								$("#gas").before('<div class="important reminder">*Please select a file for upload or completely fill out the monthly usage table with the appropriate information.</div>');
								$("#gas").before('<span class="important reminder">*   </span>');
								if(tFile == "") { 
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
								else if(!(tFile.indexOf(".csv") > 0)) {
									$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
									$("#temp").before('<span class="important reminder">*   </span>');
								}
							}
						}
						else if(gFile != "" && (gFile.indexOf(".csv") > 0)) {
							if(tFile == "") { 
								$(".reminder").remove();
								self.nextStep();
								count++;
							}
							else if(!(tFile.indexOf(".csv") > 0)) {
								$("#temp").before('<div class="important reminder">*Please upload a .csv file.</div>');
								$("#temp").before('<span class="important reminder">*   </span>');
							}
							else if(tFile.indexOf(".csv") > 0) {
								$(".reminder").remove();
								self.nextStep();
								count++;
							}
						}
					}
				}
			});
			$finish.click(function (event) {
				var emailInput = jWizard.email;
				if(emailInput.value == "") {
					$('#jWizard').submit();
				}
				else if(emailInput.value.indexOf("@") > 0) {
					$('#jWizard').submit();
				}
				else { $("emailInput").after('<div class="important reminder">*Please enter the appropriate information in the highlighted fields.</div>'); }
			});

			if (options.jqueryui.enable) {
				$cancel.button({ icons: { primary: options.jqueryui.cancelIcon } });
				$previous.button({ icons: { primary: options.jqueryui.previousIcon } });
				$next.button({ icons: { secondary: options.jqueryui.nextIcon } });
				$finish.button({ icons: { secondary: options.jqueryui.finishIcon } });
			}

			this.element.append($footer.append($('<div class="jw-buttons" />').append($cancel).append($previous).append($next).append($finish)));
		},

		/**
		 * @private
		 * @description Updates the visibility status of each of the buttons depending on the end-user's progress
		 * @see this._changeStep()
		 */
		_updateButtons: function () {
			var $steps = this.element.find(".jw-step"),
				$previous = this.element.find(".jw-button-previous"),
				$next = this.element.find(".jw-button-next"),
				$finish = this.element.find(".jw-button-finish");

			switch ($steps.index($steps.filter(":visible"))) {
			case -1:
			case 0:
				$previous.hide();
				$next.show();
				$finish.hide();
				break;

			case $steps.length - 1:
				$previous.show();
				$next.hide();
				$finish.show();
				break;

			default:
				$previous.show();
				$next.show();
				$finish.hide();
				break;
			}
		},

		_disableButtons: function () {
			this.element.find(".jw-buttons button").addClass("ui-state-disabled").attr("disabled", true);
		},

		_enableButtons: function () {
			this.element.find(".jw-buttons button").removeClass("ui-state-disabled").attr("disabled", false);
		},

		/**
		 * @private
		 * @description Updates the visibility status of each of the buttons depending on the end-user's progress
		 * @see this._changeStep()
		 */
		_destroyButtons: function () {
			this.element.find(".jw-footer").remove();
		},

		/**
		 * @property object options This is the set of configuration options available to the user.
		 */
		options: {
			titleHide: false,
			menuEnable: false,

			buttons: {
				jqueryui: {
					enable: false,
					cancelIcon: "ui-icon-circle-close",
					previousIcon: "ui-icon-circle-triangle-w",
					nextIcon: "ui-icon-circle-triangle-e",
					finishIcon: "ui-icon-circle-check"
				},
				cancelHide: false,
				cancelType: "button",
				finishType: "button",
				cancelText: "Cancel",
				previousText: "Previous",
				nextText: "Next",
				finishText: "Tune"
			},

			counter: {
				enable: false,
				type: "count",
				progressbar: false,
				location: "footer",
				startCount: true,
				startHide: false,
				finishCount: true,
				finishHide: false,
				appendText: "Complete",
				orientText: "left"
			},

			effects: {
				enable: false,
				step: {
					enable: false,
					hide: {
						type: "slide",
						options: { direction: "left" },
						duration: "fast"
					},
					show: {
						type: "slide",
						options: { direction: "left" },
						duration: "fast"
					}
				},
				title: {
					enable: false,
					hide: {
						type: "slide",
						duration: "fast"
					},
					show: {
						type: "slide",
						duration: "fast"
					}
				},
				menu: {
					enable: false,
					change: {
						type: "highlight",
						duration: "fast"
					}
				},
				counter: {
					enable: false,
					change: {
						type: "highlight",
						duration: "fast"
					}
				}
			},

			cancel: $.noop,
			previous: $.noop,
			next: $.noop,
			finish: $.noop,

			changestep: function (event, ui) {
				if (event.isDefaultPrevented()) {
					if (typeof event.nextStepIndex !== "undefined") {
						ui.wizard.jWizard("changeStep", event.nextStepIndex);
						return false;
					}
				}
			}
		}
	});
}(jQuery));

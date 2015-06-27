

$(document).ready(function() {
	
	//selecting base model
	var image = $("#homeSelect div img");
	var sqrFootage = 10000;
	
	$("input[name=size]").val(sqrFootage);
	adjustOptions("business");
	image.click(function() {
		//$("#homeSelect .current").removeClass("current");
		//$(this).addClass("current");
		//var item = $(this).attr("alt");
		
		var item = $("#homeSelect .current").attr("alt");
		
		if(item == "home") sqrFootage = 2025;
		else sqrFootage = 10000;
		$("input[name=size]").val(sqrFootage);
		
		adjustOptions(item);
		
	});
	
	$("#homeDescription div").hide(); // hide all the descriptions so they can be shown individualy
	
	
	// end of model selection
	
	
	////////////////////////////////////////// Displaying input for each resident
	$("#inputInsert").hide();
	
	// alter enter key so that form does not submit early
	$("body").delegate("input", "keypress", (function(key) {
		if(key.keyCode == 13) {
			key.preventDefault();
			$(this).focusout();
			
			var inputs = $(this).closest('form').find(':input:visible'); // get visible inputs from the same form
            inputs.eq( inputs.index(this)+ 1 ).focus(); 		// focus on the next input
			
		}
	}));
	
	$("input[name='numRes']").focusout(function() {
		var numRes = $(this).val();
		
		if(!isNaN(numRes)) {

			$("input[name^='fName'], #inputInsert br").remove(); // remove any inputs previously available
			
			if(numRes == 0) {
				//show no fName inputs and skip schedule
				$("#inputInsert").hide();
			}
			else if(numRes > 0) {
				//create the number of fName inputs specified
				$("#inputInsert").show();
				for(var i=0; i<numRes; i++) { // numRes-1 because there is already one input
					$("#inputInsert").append('<input type="text" size="20" name="fName'+i+'" placeholder="Enter name"><br>');
				}
			}
			
		}
		
	});
	
	$("#tab").hide(); // hide the template tab

	///////////////////////////////////////////////////create schedules
	$("#createSchedules").click(function() {
		var numRes = $("input[name=numRes]").val();
		if(!isNaN(numRes)) {
			//destroy tabs if tabs were already created and recreate them
			if($("#tabs ul li").size() > 0) {
				console.log("destroyed");
				$("#tabs").tabs("destroy");
				$("#tabs ul").empty();
				$("#tabs").children().remove(":not(ul, #tab)");
				
			
			}
			
			if(numRes > 0) {
				for(var i=0; i<numRes; i++) { //tabs for time tables
					var name = $("input[name=fName"+i+"]").val();
					$("#tabs ul").append("<li><a href=\"#tab" + i + "\">" + name + "</a></li>");
				
				}
			
				for(var i=0; i<numRes; i++) { //tab content
					$("#tabs").append("<div id=\"tab" + i + "\">" + $("#tab").html() + "</div>");
				}
				for(var i=0; i<numRes; i++) { // include radio buttons in tabs
					var name = $("#tab"+i+" input[type=radio]").attr("name");
					$("#tab"+i+" input[type=radio]").attr("name", name+""+i);
				}
				$("#tabs").tabs();			//create the tabs
				
				//making the table selectable
				$("table").selectable({	
					filter:"td div", 
					appendTo:"tbody",
					stop: function() {
						if($(".ui-selected").is(".selected")) { //if selecting an item already selected, present the options
							$("#dialog-option").dialog("open");
							
							//get the title of the selection and display it as the title of the modal dialog
							var className = $(".selected.ui-selected:first").attr("class");
							var rangePos = className.indexOf("range");
							var range = className.substring(rangePos, rangePos+7);
							var selection = $("."+range);
							var info = "";
							info += selection.first().html();
							$("#selection").text(info);
							
						}
						else if($(".ui-selected").is(".ui-selectee")) {
							$("#dialog-form").dialog("open");
							
							// display the selected time range in the modal dialog
							var time1 = $(".ui-selected").first().parent().parent().attr('id'); // get the time of the first item
							var time2 = $(".ui-selected").last().parent().parent().attr('id'); 	// get the time of the last item
							var displayRange = (time1 != time2);
							time1 = militaryTimeConvert(time1); //convert from military to standard time
							time2 = militaryTimeConvert(time2);
							
							var timeRange = time1;
							if(displayRange) {
								timeRange += "-" + time2;
							}
							$("#timeRange").html(timeRange);
						}
					}
				}); // end of making the table selectable
			}
		}
	}); // end of creating the schedules
	
	
	//Create the time table
	container = $(".scheduleContainer");
	createTableHeaders(container, $("#tab input:checked"));
	createTableCol(container);			
		
	
	$("#tabs").delegate('input[name^="numCols"]', "change", function() {
		var container = $(this).parent().children(".scheduleContainer");
		var checkedInput = $(this).parent().children("input:checked");
		
		//remove headers
		container.find("thead tr th").remove(); 
		//put new headers
		createTableHeaders(container, checkedInput);
		//remove cols
		container.find("tbody tr td").remove();
		//put new cols
		createTableCol(container);
	
	});
	
	// Assigning times in schedule tabel
	var i = 0;
	$("tbody tr").each(function() {
	
		if(i%4 != 0) {
			$(this).children("th").addClass("unbold");
		}
	
		var min = (i%4)*15;
		if(min == 0) {
			var min = "00";
		}
		var hour = Math.floor(i/4);
		$(this).attr("id", hour+":"+min);
	
		
		i++;
	});
	
	
	// dialog options
	
	$("#dialog-option").dialog({
		autoOpen: false,
		height:300,
		width:400,
		modal: true,
		buttons: {
			"Submit": function() {
				var className = $(".selected.ui-selected:first").attr("class");
				$(".ui-selected").removeClass("ui-selected");
				var rangePos = className.indexOf("range");
				var range = className.substring(rangePos, rangePos+7);
				var selection = $("." + range);
				
				var room = findRoom(selection);
				var selectedRoom = $("select[name=EditRooms] option:selected").val();
				
				if(room != selectedRoom) {
					selection.removeClass(room);
					selection.addClass(selectedRoom);
					var time1 = selection.first().parent().parent().attr('id'); // get the time of the first item
					var time2 = selection.last().parent().parent().attr('id'); 	// get the time of the last item
					
					selectedRoom = $("select[name=EditRooms] option:selected").html();
					
					time1 = militaryTimeConvert(time1); //convert from military to standard time
					time2 = militaryTimeConvert(time2);
					var time = time1 + "-" + time2; 	// combine times to make the range
					var output = selectedRoom + " " + time;
					selection.first().html(output);
				}
				
				$(".ui-selected").removeClass("ui-selected");
				$(this).dialog("close");
				
			},
			"Delete": function() {
				var className = $(".selected.ui-selected:first").attr("class");
				$(".ui-selected").removeClass("ui-selected");
				var rangePos = className.indexOf("range");
				var range = className.substring(rangePos, rangePos+7);
				var selection = $("." + range);
				
				var room = findRoom(selection);
				selection.removeClass("selected")
						.removeClass(range)
						.removeClass(room);
				
				selection.parent().css("border", "");
				selection.css("padding", "10px");
				selection.html("");
				
				$(this).dialog("close");
			},
			Cancel: function() {
			
				$(".ui-selected").removeClass("ui-selected");
				$(this).dialog("close");
				
			}
		},
		close: function() {
			// do something if user closes the dialog
		
		}
	});
	
	
	
	//modal dialog
	var index = 0; // index is used to index each selected range
	$("#dialog-form").dialog({
		autoOpen: false,
		height:250,
		width:300,
		modal: true,
		buttons: {
			"Submit": function() {
				//save and do stuff
				$(this).dialog("close");
				//save
				
				//show chosen room and style selection
				
				
				//////////////////////////////////////// REMEMBER: add a class to the selected (ex. zone1, zone2, ect...
				var room = $("select[name=Rooms] option:selected").html(); // get the room that was selected 
				var first = $(".ui-selected:first"); 	// get the first selected item
				var last = $(".ui-selected:last"); 		//get the last selected item
				var time1 = first.parent().parent().attr('id'); // get the time of the first item
				var time2 = last.parent().parent().attr('id'); 	// get the time of the last item
				var selected = $(".ui-selected");
				
				time1 = militaryTimeConvert(time1); //convert from military to standard time
				time2 = militaryTimeConvert(time2);
				var time = time1 + "-" + time2; 	// combine times to make the range
				var output = room + " " + time; 
				
				var firstClass = first.attr("class");
				var lastClass = last.attr("class");
				
				
				var colIndex = firstClass.indexOf("col"); 				//locate the class name col
				var firstCol = firstClass.substring(colIndex+3,colIndex+4); // col number is listed after "col"
				
				colIndex = lastClass.indexOf("col");
				var lastCol = lastClass.substring(colIndex+3,colIndex+4);
					
				
				for(var i=firstCol; i<=lastCol; i++) {
					first.css("padding", "0px");
					first.html(output);
					first.parent().css("border-top", "2px solid black");
					
					last.parent().css("border-bottom", "2px solid black");
					
					$(".ui-selected.col"+i).addClass("range"+index);
					index++;
					
					if(firstCol != lastCol) { // if there are more cols, go to the next one
						first = first.parent().next().children("div");
						last = last.parent().prev().children("div");
						
					}
				}
				
				selected.parent().css({"border-left":"2px solid black",
										"border-right":"2px solid black"});
				
				selected.removeClass("ui-selected");
				
				var className = $("select[name=Rooms] option:selected").val();
				selected.addClass(className)
						.addClass("selected");
				
			},
			Cancel: function() {
				$(this).dialog("close");
				$(".ui-selected").removeClass("ui-selected");

			}
		},
		close: function() {
			// do something when the dialog closes
		
		}
	}); // end of modal dialog
	
	
	
	
	//Google Map
	var map;
	var infowindow = new google.maps.InfoWindow();
	function initialize() {
		var mapProp = {
		  center:new google.maps.LatLng(37.508742,-100.120850),
		  zoom:4,
		  mapTypeId:google.maps.MapTypeId.ROADMAP
		  };
		map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
		createMarkers();
	}
	function createMarkers() {
		//guess user's location
		$.post("iptolatlng.php", function(data) {
			console.log(data);
			if(data != "unknown") {
				var coords = data.split(" "); //split latitude from longitude
				map.setZoom(6);
				map.setCenter(new google.maps.LatLng(coords[0], coords[1]));
			}
			$.getJSON('/autotune/map_locations.js', 
				function(data) {
					var obj = data.weatherstations;
					for(var i=0; i<obj.length; i++) {
						var place = obj[i].city + ", " + obj[i].state;
						placeMark(place, obj[i].climateZone, obj[i].latitude, obj[i].longitude, obj[i].weatherFile);
					}
				}
			);
		});
	}
	function placeMark(location, climateZone, lat, lng, weatherFile) {
		var marker = new google.maps.Marker({
			map: map,
			position: new google.maps.LatLng(lat, lng),
			title: location,
			icon: './pictures/marker(white).png'
		});
		
		google.maps.event.addListener(marker, 'click', function() {
			infowindow.close();
			infowindow.setContent(this.title);
			
			map.setZoom(6);
			map.setCenter(marker.getPosition());
			infowindow.open(map, marker);
			// give location here! //////////////////////////////////////
			$("input[name=location]").val(this.title);
			$("#locationOutput").text(this.title);
			$("input[name=weatherFile]").val(weatherFile);
			$("input[name=climateZone]").val(climateZone);
			//could insert weather string into a hidden input here -> take the string as an parameter
		});
	}
	
	
	var initialized = false;
	$("body").delegate(".jw-button-next", "click", function() {
		
		if($("#map").css("display") != "none" && !initialized) {
			//make the google maps width and height fit the container
			var availHeight = $("#googleMap").parent().height();
			var usedHeight = 0;
			$("#googleMap").siblings().each(function() {
				usedHeight += $(this).height();
			});
			availHeight = availHeight - usedHeight;
			
			var width = $("#googleMap").parent().css('width'); //css('width') gives the value in pixels
			
			$("#googleMap").css('height', availHeight + "px");
			$("#googleMap").css('width', width);
			
			initialize();
			initialized = true;
		}
	});
	//google.maps.event.addDomListener(window, 'load', initialize);
	// end of Google Map section

	
	
	//accordian
	$("#accordion").accordion({ 
		collapsible: true, 
		active: 0,
		heightStyle: "content"
	});
	
	//create monthly inputs for energy usage
	var months = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");
	
	appendAsFloats("#energyInputs", months, "energyUsage", "Energy Usage", "kWh"); 
	appendAsFloats("#gasInputs", months, "gasUsage", "Gas Usage", "CCF"); 

	function appendAsFloats(id, labelArray, inputName, placeholder, units) { // appends as floating elements
		/*	id - id of element to append to
		 * 	isVertical - Boolean indicating orientation of table elements
		 * 		True - elements go in order vertically and continue in the next column
		 * 		False - elements go in order horizontally and continue in the next row
		 * 	numRow - number of rows you would like the table to have
		 * 	numCol - number of cols you would like the table to have
		 * 	labelArray - array containing labels, must be numerically indexed
		 * 	inputName - name of each input (will be made as an array)
		 * 	placeholder - placeholder for each element
		 * 	units - unit for inputs, will be appended to the input tag
		 */
		return appendInputs(id, false, false, labelArray.length, 1, labelArray, inputName, placeholder, units);
	}
	
	function appendInTableFormat(id, isVertical, numRow, numCol, labelArray, inputName, placeholder, units) {
		/*	id - id of element to append to
		 * 	isVertical - Boolean indicating orientation of table elements
		 * 		True - elements go in order vertically and continue in the next column
		 * 		False - elements go in order horizontally and continue in the next row
		 * 	numRow - number of rows you would like the table to have
		 * 	numCol - number of cols you would like the table to have
		 * 	labelArray - array containing labels, must be numerically indexed
		 * 	inputName - name of each input (will be made as an array)
		 * 	placeholder - placeholder for each element
		 * 	units - unit for inputs, will be appended to the input tag
		 */
		return appendInputs(id, isVertical, true, numRow, numCol, labelArray, inputName, placeholder, units);
		
	} 
	
	function appendInputs(id, isVertical, inTableFormat, numRow, numCol, labelArray, inputName, placeholder, units) {
		// inTableFormat - boolean indicating whether to append in table format or as floating elements
		if(numRow*numCol > labelArray.length) return false; // table cannot be larger than the number of labels
		$(id).append("<table>");
		for(var i=0; i<numRow; i++) {
			$(id).append("<tr>");
			for(var j=0; j<numCol; j++) {
				if(isVertical) 	var key = i+(j*numRow);
				else 			var key = j+(i*numCol);
				
				if(inTableFormat) {
					$(id).append("<td><label>" + labelArray[key] + ' </label></td><td><input size="10" type="text" name="' + inputName + '[' + key + ']" placeholder="' + placeholder + '">' + units + ' </td>');
				}
				else {
					$(id).append('<div style="float:left;width:180px;"><div><label>' + labelArray[key] + '</label></div><input size="10" type="text" name="' + inputName + '[' + key + ']" placeholder="' + placeholder + '">' + units + '</div>');
				}
			}
			$(id).append("</tr>");
		}
		$(id).append("</table>");
		return true;
	}
		
	
	function adjustOptions(type) {
		var options = $("select[name='idf[building_type]'] option");
		options.hide();
		var first = true;
		options.each(function() {
			var str = $(this).attr("class");
			if(str.search(type) != -1) { //if you can find the type within the class
				$(this).show();
				if(first) {
					$(this).prop("selected", true);
					first = false;
				}
			}
		});
	}
	
	
	function createTableHeaders(container, $checkedInput) {
		numCol = $checkedInput.val();
		var header;
		if(numCol == 2) {
			//set Weekday/Weekend headers for table
			header = new Array("Weekdays","Weekends/Holidays");
		}
		if(numCol == 7) {
			//set each day as a header for the table
			header = new Array("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat");
		}
		container.find("thead tr").append("<th></th>");
		for(var i=0; i<numCol; i++) {
			
			container.find("thead tr").append("<th>" + header[i] + "</th>");
		}
	}
	
	function createTableCol($container) {
		$container.find("tbody tr").each(function() {
			numCol = $container.parent().children("input[type=radio]:checked").val();
			
			for(var i=0; i<numCol; i++) {
				$(this).append("<td><div class=\"ui-selectee\"> </div></td>");
			}
		});
		var i = 0;
		$container.find("td div").each(function() {
			numCol = $container.parent().children("input[type=radio]:checked").val();
			colNum = i%numCol; // replace 2 with the number of columns //////////////////////////
			$(this).addClass("col"+colNum);
			i++;
		});
	}
	
	
	function militaryTimeConvert(time) {
		var colon = time.indexOf(":");
		var hour = time.substring(0, colon);
		var min = time.substring(colon+1);
		hour = hour.valueOf();
		hour -= 12;
		if(hour < 0) {
			hour += 12;
			min += "AM";
		}
		else if (hour == 0) {
			hour += 12;
			min += "PM";
		}
			
		else
			min += "PM";
			
		if(hour == 0)
			hour = 12;
		
		return (hour + ":" + min);
	}
	
	function findRoom(jQObj) {
		var rooms = new Array("bedroom", "kitchen", "bathroom", "diningRoom", "livingRoom");
		for(var i = 0; i<rooms.length; i++) {
			if(jQObj.is("." + rooms[i])) {
				return rooms[i];
			}
		}
		
	}

});







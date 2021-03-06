	$(document).ready(function(){
		var ws;
		var has_error = false;
		var num = 0;
		var last = 0;
		announce = function(c,m) {
			var inf = $("div#info");
			inf.empty();
			// var li = $('<div class="alert alert-'+c+'" />');
			var li = $('<div/>');
			num = num+1;
			var n = num;
			li.attr('id', 'alert-'+n)
			li.addClass('alert');
			li.addClass('alert-'+c);
			// li.addClass('fade');
			// li.addClass('fade in');
			li.hide();
			li.text(m);
			inf.prepend(li);
			li.fadeIn(300);
			$('#page').scrollTop(0);
			if (last > 0)
			{
				$('#alert-'+last).alert('close')
			}
			if (c == "danger") {
				last = n;
			} else {
				setTimeout(function(){ 
					$('#alert-'+n).alert('close')
				}, 2000);
			}
		}
		//$('form#sender').submit(function(event){
		//	ws.send(JSON.stringify({"type":["note"],"data": $('input#data').val() }));
		//	$('textarea#data').val("");
		//	return false;
		//});
		if ("WebSocket" in window && "moat" in window && "ws_url" in window.moat) {
			announce("info","Connecting …")
			var ws = new WebSocket(window.moat.ws_url +"/api/control");
			var backlogging = true;

			ws.onmessage = function (msg) {
				var m = $.parseJSON(msg.data);
				if (!('action' in m)) {
					announce("warning","Unknown message: " + m)
				} else if (m.action == 'error') {
					announce("danger",m.msg)

				} else if (m.action == 'replace') {
					var f = $('#'+m.id);
					if (f.length == 0) {
						announce("danger","Content ID "+m.id+" not found.");
						return;
					}
					var d = $(m.data);
					d.attr("id",m.id)
					if (m.keep) {
						m.keep.split('').forEach(function(c) {
							var dd = d.find("#"+c+m.id)
							var ff = f.find("#"+c+m.id)
							ff.children().each(function(i,x) {
								dd.append(x);
							});
						});
					}
					f.replaceWith(d);

				} else if (m.action == 'insert') {
					var f = $('#'+m.parent);
					if (f.length == 0)  {
						announce("danger","Content ID "+m.parent+" for "+m.id+" not found.");
						return;
					}
					var d = $(m.data);
					d.attr("id",m.id);
					// d.css("height";"0px");
					var todo = true;
					if (m.sortkey) {
						d.attr("sortkey",m.sortkey);
						f.children().each(function(i,ff) {
							if(todo) {
								if (ff.getAttribute("sortkey") < m.sortkey)
									return;
								d.insertBefore(ff);
								todo = false;
							}
						});

					}
					if (todo)
						f.append(d);
					// d.animate({height: d.prop('scrollHeight')}, 300, "swing", function(){ d.css("height","");});

				} else if (m.action == 'update') {
					(function(m) {
					var d = $(m.data);
					d.attr("id",m.id)
					var dly = m.fade || 400;
					var f = $('#'+m.id);
					if (f.length == 0) {
						announce("danger","No content for "+m.id+" found.");
						return;
					}
					f.fadeOut(dly, function() {
						f.replaceWith(d);
						f.fadeIn(dly);
					});
					})(m);

				} else if (m.action == 'delete') {
					f = $('#'+m.id);
					if (f.length == 0) {
						announce("warning","No content for "+m.id+" found.");
						return;
					}
					f.fadeOut(300, function() {
						f.animate({height: "0px"},300,"swing",function() {
							f.remove();
						});
					});

				} else if (m.action == 'clear') {
					f = $('#'+m.id);
					if (f.length == 0) {
						announce("warning","No content for "+m.id+" found.");
						return;
					}
					f.fadeOut(300, function() {
						f.animate({height: "0px"},300,"swing" ,function() {
							f.empty();
							f.css("height","");
						});
					});

				} else {
					console.log("IN",m);
					announce("warning","Unknown action: " + m.action)
				}
			};
			ws.onopen = function (msg) {
				has_error = false;
			    announce("success","Connected. Waiting for instructions …");
				window.to_moat = function(msg) {
					ws.send(JSON.stringify(msg));
				};
				ws.send(JSON.stringify({"action":"locate","location": window.location.hash }));
			};
			var msg_dead = function(msg) {
				announce("warning","Not connected. Reload before doing this.");
			};

			ws.onerror = function (msg) {
				has_error = true;
				window.to_moat = msg_dead;
				announce("danger","Connection error! Please reload this page.");
			};
			ws.onclose = function (msg) {
				if (has_error) { return; }
				window.to_moat = msg_dead;
				announce("danger","Connection closed.");
			};
		} else if ("WebSocket" in window) {
			announce("danger","Internal error! Please try again later.");
		} else {
			announce("info","Your browser does not support WebSockets. Sorry.");
		}


		// $.idleTimer(300000); // Hochscrollen nach 5min
		// $(document).bind("idle.idleTimer", function(){
			// $('#page').scrollTop(0);
		// });

	});

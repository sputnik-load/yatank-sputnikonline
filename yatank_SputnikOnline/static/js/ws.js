(function() {
  var app, collect_subtree,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  app = angular.module("ng-tank-report", ["angular-rickshaw"]);

  collect_subtree = function(storage, subtree, ts) {
    var key, node, _results;
    _results = [];
    for (key in subtree) {
      node = subtree[key];
      if (typeof node === 'number' || typeof node === 'array') {
        _results.push(storage[key].push({
          x: ts,
          y: node
        }));
      } else {
        _results.push(collect_subtree(storage[key], node, ts));
      }
    }
    return _results;
  };

  updateConsoleBlock = function(block, id) {
    var content = "";
    var i;
    for (i = 0; i < block.length; ++i) {
      content += block[i] + "</br>";
    }
    angular.element("div#" + id).html(content);
  }

  updateHTMLContent = function(con_out) {
    var date = new Date(con_out.cur_time * 1000);
    var loc_dt = date.toLocaleDateString();
    var loc_tm = date.toLocaleTimeString();
    var content = "Current Time: " + loc_dt + " " + loc_tm;
    angular.element("div#current_time").html(content);
    angular.element("#plugin_info").html("Yandex.Tank SputnikOnline " + con_out.plugin.version + " report");
    updateConsoleBlock(con_out.blocks.times_dist, "console_rps");
    updateConsoleBlock(con_out.blocks.http, "console_http");
    updateConsoleBlock(con_out.blocks.net, "console_net");
    updateConsoleBlock(con_out.blocks.cases, "console_cases");
    updateConsoleBlock(con_out.blocks.quantiles, "console_quantiles");
    updateConsoleBlock(con_out.blocks.answsizes, "console_answsizes");
    updateConsoleBlock(con_out.blocks.avgtimes, "console_avgtimes");
    updateConsoleBlock(con_out.widgets, "console_widgets");
  }

  app.controller("TankReport", function($scope, $element) {
    var conn;
    $scope.status = "Disconnected";
    $scope.data = document.cached_data.data;
    $scope.uuid = document.cached_data.uuid;
    $scope.updateData = function(tankData) {
      var data, storage, storages, ts;
      for (ts in tankData) {
        storages = tankData[ts];
        for (storage in storages) {
          if (storage === "widgets" || storage === "blocks" || storage === "plugin")
            continue;
          data = storages[storage];
          collect_subtree($scope.data[storage], data, +ts);
        }
      }
      return $scope.$broadcast('DataUpdated');
    };
    $scope.con_out = {
      name: "Console Output",
      cur_time: undefined,
      blocks: {},
      widgets: [],
      plugin: {}
    }; 
    $scope.buildSeries = function() {
      var areaGraphs, data, groupName, groups, hostname, name, overallData, series;
      if ($scope.data.responses && $scope.data.responses.overall) {
        overallData = $scope.data.responses.overall;
      } else {
        overallData = {};
        setTimeout((function() {
          return location.reload(true);
        }), 3000);
      }
      areaGraphs = ['CPU', 'Memory'];
      $scope.monitoringData = (function() {
        var _ref, _results;
        _ref = $scope.data.monitoring;
        _results = [];
        for (hostname in _ref) {
          groups = _ref[hostname];
          _results.push({
            hostname: hostname,
            groups: (function() {
              var _results1;
              _results1 = [];
              for (groupName in groups) {
                series = groups[groupName];
                _results1.push({
                  name: groupName,
                  features: {
                    palette: 'spectrum14',
                    hover: {},
                    xAxis: {},
                    yAxis: {},
                    legend: {
                      toggle: true,
                      highlight: true
                    }
                  },
                  options: {
                    renderer: __indexOf.call(areaGraphs, groupName) >= 0 ? 'area' : 'line'
                  },
                  series: (function() {
                    var _results2;
                    _results2 = [];
                    for (name in series) {
                      data = series[name];
                      _results2.push({
                        name: name,
                        data: data
                      });
                    }
                    return _results2;
                  })()
                });
              }
              return _results1;
            })()
          });
        }
        return _results;
      })();
      $scope.quantiles = {
        name: "Response time quantiles",
        features: {
          palette: 'classic9',
          hover: {},
          xAxis: {},
          yAxis: {},
          legend: {
            toggle: true,
            highlight: true
          }
        },
        options: {
          renderer: 'area',
          stack: false,
          height: $element[0].offsetHeight - 45 - 62
        },
        series: ((function() {
          var _ref, _results;
          _ref = overallData.quantiles;
          _results = [];
          for (name in _ref) {
            data = _ref[name];
            _results.push({
              name: name,
              data: data
            });
          }
          return _results;
        })()).sort(function(a, b) {
          if (parseFloat(a.name) <= parseFloat(b.name)) {
            return 1;
          } else {
            return -1;
          }
        })
      };
      return $scope.rps = {
        name: "Responses per second",
        features: {
          palette: 'spectrum14',
          hover: {},
          xAxis: {},
          yAxis: {},
          legend: {
            toggle: true,
            highlight: true
          }
        },
        options: {
          renderer: 'line'
        },
        series: [
          {
            name: 'RPS',
            data: overallData.RPS
          }
        ]
      };
    };
    $scope.buildSeries();
    conn = new io.connect("http://" + window.location.host, {
      'reconnection limit': 1000,
      'max reconnection attempts': '5'
    });
    setInterval((function() {
      return conn.emit('heartbeat');
    }), 3000);
    conn.on('connect', (function(_this) {
      return function() {
        console.log("Connection opened...");
        $scope.status = "Connected";
        return $scope.$apply();
      };
    })(this));
    conn.on('disconnect', (function(_this) {
      return function() {
        console.log("Connection closed...");
        $scope.status = "Disonnected";
        return $scope.$apply();
      };
    })(this));
    conn.on('reload', (function(_this) {
      return function() {
        return location.reload(true);
      };
    })(this));
    return conn.on('message', (function(_this) {
      return function(msg) {
        var tankData;
        tankData = JSON.parse(msg); 
        var ts = [];
        for (var t in tankData.data) {
          if (tankData.data.hasOwnProperty(t)) {
            ts.push(t)
          }
        }
        if (ts.length == 1) {
          var timestamp = ts[0];
          $scope.con_out.cur_time = timestamp;
          var tank_blocks = tankData.data[timestamp].blocks;
          for (var block_name in tank_blocks) {
            if (tank_blocks.hasOwnProperty(block_name))
              $scope.con_out.blocks[block_name] = tank_blocks[block_name]
          }
          if ("widgets" in tankData.data[timestamp]) {
            $scope.con_out.widgets = tankData.data[timestamp].widgets;
          }
          if ("plugin" in tankData.data[timestamp]) {
            $scope.con_out.plugin = tankData.data[timestamp].plugin;
          }
        }
        if (tankData.uuid && $scope.uuid !== tankData.uuid) {
          return location.reload(true);
        } else {
          updateHTMLContent($scope.con_out);
          return $scope.updateData(tankData.data);
        }
      };
    })(this));
  });

}).call(this);

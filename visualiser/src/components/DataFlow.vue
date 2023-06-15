<template>
  <div id="container" className="d-flex flex-column justify-content-left align-items-left"  >
    <div id="button-bar" style="background-color: #56a6ef" >
      <label htmlFor="myfile">Import from file:</label><input type="file" @change="uploadFile"
                                                              accept="application/json"/>
      <button id="btnImportRest">Import over Rest</button>
      <button id="btnExportJson">Export to JSON</button>
      <h4 v-if="loading">Loading</h4>
      <h4 v-if="error" className="text-danger">{{ error }}</h4>
    </div>

    <div id="cy" className="cy"></div>

  </div>
</template>

<style lang="scss">
#container {
  height: 100%;
  width: 100%;
}

#cy {
  height: 1000px;
  width: 2000px;
}
</style>


<script>
import cydagre from "cytoscape-dagre";
import cytoscape from "cytoscape";
import contextMenus from 'cytoscape-context-menus';
import edgehandles from 'cytoscape-edgehandles';
import popper from 'cytoscape-popper';
import 'cytoscape-context-menus/cytoscape-context-menus.css';
import {computed, ref} from "vue";
import axios from "axios";

cytoscape.use(contextMenus);
cytoscape.use(edgehandles);
cytoscape.use(popper);

export default {
  name: "DataFlow",
  data() {
    return {
      loading: false,
      error: null,
      button: '<button id="btnExportJson"></button>',
      button2: '<button id="btnImportRest"></button>',
    };
  },
  mounted() {
    const imr = document.getElementById("btnImportRest").addEventListener("click", this.importfromrest);
  },
  methods: {
    importfromrest: function (event) {
      let text;
      let uri = prompt("Please enter the uri:", "");
      if (uri == null || uri == "") {
        return;
      } else {
        text = uri;
      }
      getDataPromise()
          .then(res => this.drawGraph(res));

      function getDataPromise() {
        return axios({
          url: text,
          method: 'get',
          timeout: 8000,
          headers: {
            'Content-Type': 'application/json',
          }
        })
            .then(res => res.data)
            .catch(err => console.error(err))
      }
    },
    uploadFile: function (event) {
      const file = ref(null);
      const fileName = computed(() => file.value?.name);
      const fileExtension = computed(() => fileName.value?.substr(fileName.value?.lastIndexOf(".") + 1));
      const fileMimeType = computed(() => file.value?.type);
      file.value = event.target.files[0];
      const reader = new FileReader();
      reader.readAsText(file.value);
      reader.onload = async () => {
        const jsonData = JSON.parse(reader.result);
        this.drawGraph(jsonData);
      };
    },
    drawGraph: function (jsonData) {
      const bmd = document.getElementById("btnExportJson").addEventListener("click", savedata);
      let dispLayout = 'dagre';
      if (jsonData.nodes.some(obj => obj.hasOwnProperty("position"))) {
        dispLayout = 'preset';
      }
      cydagre(cytoscape);
      const cy = cytoscape({
        container: document.getElementById("cy"),
        boxSelectionEnabled: false,
        autounselectify: true,
        style: cytoscape
            .stylesheet()
            .selector("node")
            .css({
              shape: "roundrectangle",
              height: 40,
              width: "data(width)",
              "background-color": (node) =>
                  node.data("active") ? "green" : "white",
              color: (node) => (node.data("active") ? "white" : "black"),
              "border-color": "gray",
              "border-width": 3,
              "border-radius": 4,
              content: "data(name)",
              "text-wrap": "wrap",
              "text-valign": "center",
              "text-halign": "center",
            })
            .selector("edge")
            .css({
              "text-outline-color": "white",
              "text-outline-width": 3,
              "text-valign": "top",
              "text-halign": "left",
              "curve-style": "bezier",
              width: 3,
              "target-arrow-shape": "triangle",
              "line-color": "gray",
              "target-arrow-color": "gray",
            })
            .selector(".eh-handle")
            .css({
              "background-color": "red",
              "width": 12,
              "height": 12,
              "shape": "ellipse",
              "overlay-opacity": 0,
              "border-width": 12, // makes the handle easier to hit
              "border-opacity": 0
            })
            .selector(".eh-hover")
            .css({"background-color": "red"})
            .selector(".eh-source")
            .css({
              "border-width": 2,
              "border-color": "red"
            })
            .selector(".eh-target")
            .css({
              "border-width": 2,
              "border-color": "red"
            })
            .selector(".eh-preview, .eh-ghost-edge")
            .css({
              'background-color': 'red',
              'line-color': 'red',
              'target-arrow-color': 'red',
              'source-arrow-color': 'red'
            })
            .selector(".eh-ghost-edge.eh-preview-active")
            .css({'opacity': 0}),
        elements: {
          nodes: jsonData.nodes,
          edges: jsonData.edges,
        },
        layout: {
          name: dispLayout,
          spacingFactor: 1.5,
          rankDir: "LR",
          fit: true,
        },
      }).on('cxttap', function (event) {
        if (allSelected('node')) {
          contextMenu.hideMenuItem('select-all-nodes');
          contextMenu.showMenuItem('unselect-all-nodes');
        } else {
          contextMenu.hideMenuItem('unselect-all-nodes');
          contextMenu.showMenuItem('select-all-nodes');
        }
        if (allSelected('edge')) {
          contextMenu.hideMenuItem('select-all-edges');
          contextMenu.showMenuItem('unselect-all-edges');
        } else {
          contextMenu.hideMenuItem('unselect-all-edges');
          contextMenu.showMenuItem('select-all-edges');
        }
      });  //cytoscape container

      //edgehandles
      let defaults = {
        canConnect: function( sourceNode, targetNode ){
          // whether an edge can be created between source and target
          return !sourceNode.same(targetNode); // e.g. disallow loops
        },
        edgeParams: function( sourceNode, targetNode ){
          // for edges between the specified source and target
          // return element object to be passed to cy.add() for edge
          return {};
        },
        hoverDelay: 150, // time spent hovering over a target node before it is considered selected
        snap: true, // when enabled, the edge can be drawn by just moving close to a target node (can be confusing on compound graphs)
        snapThreshold: 50, // the target node must be less than or equal to this many pixels away from the cursor/finger
        snapFrequency: 15, // the number of times per second (Hz) that snap checks done (lower is less expensive)
        noEdgeEventsInDraw: true, // set events:no to edges during draws, prevents mouseouts on compounds
        disableBrowserGestures: true // during an edge drawing gesture, disable browser gestures such as two-finger trackpad swipe and pinch-to-zoom
      };

      let eh = cy.edgehandles(defaults);
      let popperEnabled = false;
      let popperNode;
      let popper;
      let popperDiv;
      let started = false;

      function start() {
        eh.start(popperNode)
      }

      function stop() {
        eh.stop();
      }

      function setHandleOn(node) {
        if (started) {
          return;
        }

        removeHandle(); // rm old handle

        let popperNode = node;

        let popperDiv = document.createElement('div');
        popperDiv.classList.add('popper-handle');
        popperDiv.addEventListener('mousedown', start);
        document.body.appendChild(popperDiv);

        let popper = node.popper({
          content: popperDiv,
          popper: {
            placement: 'top',
            modifiers: [
              {
                name: 'offset',
                options: {
                  offset: [0, -10],
                },
              },
            ]
          }
        });
      }

      function removeHandle() {
        if (popper) {
          popper.destroy();
          let popper = null;
        }

        if (popperDiv) {
          document.body.removeChild(popperDiv);
          let popperDiv = null;
        }

        let popperNode = null;
      }

      cy.on('mouseover', 'node', function (e) {
        setHandleOn(e.target);
      });

      cy.on('grab', 'node', function () {
        removeHandle();
      });

      cy.on('tap', function (e) {
        if (e.target === cy) {
          removeHandle();
        }
      });

      cy.on('zoom pan', function () {
        removeHandle();
      });

      window.addEventListener('mouseup', function (e) {
        stop();
      });

      cy.on('ehstart', function () {
        let started = true;
      });

      cy.on('ehstop', function () {
        let started = false;
      });


      let allSelected = function (type) {
        if (type == 'node') {
          return cy.nodes().length == cy.nodes(':selected').length;
        } else if (type == 'edge') {
          return cy.edges().length == cy.edges(':selected').length;
        }
        return false;
      }

      let selectAllOfTheSameType = function (type) {
        if (type == 'node') {
          cy.nodes().select();
        } else if (type == 'edge') {
          cy.edges().select();
        }
      };
      let unselectAllOfTheSameType = function (type) {
        if (type == 'node') {
          cy.nodes().unselect();
          ;
        } else if (type == 'edge') {
          cy.edges().unselect();
        }
      };

      let contextMenu = cy.contextMenus({
        menuItems: [
          {
            id: 'addconnection',
            content: 'Add connection',
            tooltipText: 'Add connection',
            image: {src: "../assets/remove.svg", width: 12, height: 12, x: 6, y: 4},
            selector: 'node',
            onClickFunction: function (event) {
              let target = event.target || event.cyTarget;
              eh.start(event.target);
              //contextMenu.showMenuItem('undo-last-remove');
            },
            hasTrailingDivider: true
          },
          {
            id: 'remove',
            content: 'remove',
            tooltipText: 'remove',
            image: {src: "../assets/remove.svg", width: 12, height: 12, x: 6, y: 4},
            selector: 'node, edge',
            onClickFunction: function (event) {
              let target = event.target || event.cyTarget;
              let removed = target.remove();

              contextMenu.showMenuItem('undo-last-remove');
            },
            hasTrailingDivider: true
          },
          {
            id: 'undo-last-remove',
            content: 'undo last remove',
            selector: 'node, edge',
            show: false,
            coreAsWell: true,
            onClickFunction: function (event) {
              if (removed) {
                removed.restore();
              }
              contextMenu.hideMenuItem('undo-last-remove');
            },
            hasTrailingDivider: true
          },
          {
            id: 'color',
            content: 'change color',
            tooltipText: 'change color',
            selector: 'node',
            hasTrailingDivider: true,
            submenu: [
              {
                id: 'color-blue',
                content: 'blue',
                tooltipText: 'blue',
                onClickFunction: function (event) {
                  let target = event.target || event.cyTarget;
                  target.style('background-color', 'blue');
                },
                submenu: [
                  {
                    id: 'color-light-blue',
                    content: 'light blue',
                    tooltipText: 'light blue',
                    onClickFunction: function (event) {
                      let target = event.target || event.cyTarget;
                      target.style('background-color', 'lightblue');
                    },
                  },
                  {
                    id: 'color-dark-blue',
                    content: 'dark blue',
                    tooltipText: 'dark blue',
                    onClickFunction: function (event) {
                      let target = event.target || event.cyTarget;
                      target.style('background-color', 'darkblue');
                    },
                  },
                ],
              },
              {
                id: 'color-green',
                content: 'green',
                tooltipText: 'green',
                onClickFunction: function (event) {
                  let target = event.target || event.cyTarget;
                  target.style('background-color', 'green');
                },
              },
              {
                id: 'color-red',
                content: 'red',
                tooltipText: 'red',
                onClickFunction: function (event) {
                  let target = event.target || event.cyTarget;
                  target.style('background-color', 'red');
                },
              },
            ]
          },
          {
            id: 'add-node',
            content: 'add node',
            tooltipText: 'add node',
            image: {src: "../assets/add.svg", width: 12, height: 12, x: 6, y: 4},
            coreAsWell: true,
            onClickFunction: function (event) {
              let text;
              let nodename = prompt("Please enter a node name:", "");
              if (nodename == null || nodename == "") {
                return;
              } else {
                text = nodename;
              }

              let nodedata = {name: text, description: "", active: false, width: 140};

              let pos = event.position || event.cyPosition;

              cy.add({
                group: 'nodes',
                data: nodedata,
                position: {
                  x: pos.x,
                  y: pos.y
                },
              });

            }
          },
          {
            id: 'select-all-nodes',
            content: 'select all nodes',
            selector: 'node',
            coreAsWell: true,
            show: true,
            onClickFunction: function (event) {
              selectAllOfTheSameType('node');

              contextMenu.hideMenuItem('select-all-nodes');
              contextMenu.showMenuItem('unselect-all-nodes');
            }
          },
          {
            id: 'unselect-all-nodes',
            content: 'unselect all nodes',
            selector: 'node',
            coreAsWell: true,
            show: false,
            onClickFunction: function (event) {
              unselectAllOfTheSameType('node');

              contextMenu.showMenuItem('select-all-nodes');
              contextMenu.hideMenuItem('unselect-all-nodes');
            }
          },
          {
            id: 'select-all-edges',
            content: 'select all edges',
            selector: 'edge',
            coreAsWell: true,
            show: true,
            onClickFunction: function (event) {
              selectAllOfTheSameType('edge');

              contextMenu.hideMenuItem('select-all-edges');
              contextMenu.showMenuItem('unselect-all-edges');
            }
          },
          {
            id: 'unselect-all-edges',
            content: 'unselect all edges',
            selector: 'edge',
            coreAsWell: true,
            show: false,
            onClickFunction: function (event) {
              unselectAllOfTheSameType('edge');
              contextMenu.showMenuItem('select-all-edges');
              contextMenu.hideMenuItem('unselect-all-edges');
            }
          }
        ],
        menuItemClasses: ['custom-menu-item'],
        contextMenuClasses: ['custom-context-menu']
      });

      function savedata() {

        let dataofinterest = Object.values(cy.elements().jsons());
        let dataofinterest2 = Object.values(cy.nodes().jsons());
        const data1 = {}
        data1.nodes = [];
        data1.edges = [];
        dataofinterest.forEach(function (item, index) {
          if (item.group == 'nodes') {
            data1.nodes.push(item);
          }
          if (item.group == 'edges') {
            delete item['data'].id;
            data1.edges.push(item);
          }
        });

        const fixed = JSON.stringify(data1, (key, value) => {
          if (!isNaN(value) && value !== "" && typeof value != "boolean")
            value = Number(value)
          return value
        })

        let tzstamp = new Date().toISOString().slice(0, 19).replace(new RegExp(/T|:+/g, "gm"), "-");
        const blob = new Blob([fixed], {type: 'application/json charset=utf-8'});
        const e = document.createEvent('MouseEvents'),
            a = document.createElement('a');
        a.download = "cyto-data" + tzstamp + ".json";
        a.href = window.URL.createObjectURL(blob);
        a.dataset.downloadurl = ['text/json', a.download, a.href].join(':');
        e.initEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
        a.dispatchEvent(e);

      }

    } //end draw graph,
  },
};
</script>

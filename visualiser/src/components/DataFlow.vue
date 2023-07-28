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

    <div className="popup-box" id="popup-box" size="small">
    </div>

    <div id="cy" className="cy"></div>

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

#popup-box .modal {
  display: flex; /* Hidden by default */
  position: fixed; /* Stay in place */
  z-index: 1; /* Sit on top */
  left: 0;
  top: 0;
  width: 100%; /* Full width */
  height: 100%; /* Full height */
  overflow: auto; /* Enable scroll if needed */
  background-color: rgb(0, 0, 0); /* Fallback color */
  background-color: rgba(0, 0, 0, 0.4); /* Black w/ opacity */
}

#popup-box .modal-content {
  background-color: #fefefe;
  left: 25%;
  width: 50%;
  height: 80%;
  padding: 20px;
  border: 1px solid #888;
  /* Could be more or less, depending on screen size */
}

#popup-box .nodedetails {
  min-height: 40px;
  text-align:center;
  margin: 1px;
}

#popup-box .buttonbar {
  padding: 2%;
  margin-right: 5%;
  margin-bottom: 2%;
  display: inline-block;
  width: 100%;
}

#popup-box .selected {
  background-color: gainsboro;
  border-color: red;
}
.selectdeleteimg {
  width: 24px;
  height: 24px;
  fill: red;
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
      if (jsonData.elements.nodes.some(obj => obj.hasOwnProperty("position"))) {
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
          nodes: jsonData.elements.nodes,
          edges: jsonData.elements.edges,
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
            id: 'edit-node',
            content: 'view / edit properties',
            coreAsWell: false,
            image: {src: "../assets/edit.svg", width: 12, height: 12, x: 6, y: 4},
            selector: 'node',
            onClickFunction: function (event) {
              let node2edit = event.target || event.cyTarget;
              let node2editdata = node2edit.json().data

              const editNode = (label) => {

                function compare(original, copy) {
                  for (let [k, v] of Object.entries(original)) {
                    if (typeof v === "object" && v !== null) {
                      if (!copy.hasOwnProperty(k)) {
                        copy[k] = v;
                      } else {
                        compare(v, copy?.[k]);
                      }
                    } else {
                      if (Object.is(v, copy?.[k])) {
                        delete copy?.[k];
                      }
                    }
                  }
                  return copy;
                }

                console.log("%%%% ", self.nodedata)

                const diff = compare(node2editdata, JSON.parse(JSON.stringify(self.nodedata)));
                console.log("$$$$$ ", diff)

                if (Object.keys(diff).length  !== 0 ) {
                  console.log ("Action - ", Object.keys(diff).length )
                  node2edit.data(self.nodedata);
                }
              }

              const addProperty = () => {

                const div2append = document.querySelector('#customprops')
                const numrows = div2append.childNodes.length + 1
                const row = document.createElement('div')
                const col1 = document.createElement('div')
                const col2 = document.createElement('div')
                const col3 = document.createElement('div')
                const selectdelete = document.createElement('span')
                const img = document.createElement('img')

                row.className='row'
                row.id = numrows
                col1.className="col-sm-3 col-md-3 col-lg-3"
                col2.className="col-sm-3 col-md-3 col-lg-3"
                col3.className="col-sm-3 col-md-3 col-lg-3"

                img.setAttribute("img src", "../assets/remove.svg")
                img.classList.add('selectdeleteimg')
                selectdelete.addEventListener('click', toggleSelect.bind(null, numrows, '#customprops'))
                selectdelete.appendChild(img)

                div2append.appendChild(row)
                const propname = document.createElement('input');
                const propvalue = document.createElement('input');
                propname.setAttribute('name', 'propname')
                propvalue.setAttribute('name', 'propvalue')
                propname.setAttribute('id', Date.now().toString())
                propvalue.setAttribute('id', Date.now().toString())
                propname.setAttribute('placeholder', 'Enter the name of your property')
                propvalue.setAttribute('placeholder', 'Enter the value of your property')
                row.appendChild(col1)
                col1.appendChild(propname)
                propname.focus()
                row.appendChild(col2)
                col2.appendChild(propvalue)
                row.appendChild(col3)
                col3.appendChild(selectdelete)
                const addPropBtn = document.getElementById("addPropBtn")
                const editBtn = document.getElementById("editBtn")
                addPropBtn.textContent = "Add another"
                editBtn.disabled = true

              }

              const toggleSelect = (rowindex, divtag) => {
                const divofintrest = document.querySelector( divtag)
                const selectedrow = divofintrest.childNodes[rowindex]
                const okBtn = document.getElementById('okBtn');
                const editBtn = document.getElementById('editBtn');
                if ( selectedrow.classList.contains('selected')){
                  selectedrow.classList.remove('selected', 'border', 'border-danger')
                  for (const childnode of divofintrest.childNodes) {
                    if (childnode.classList.contains('selected')) {
                      okBtn.textContent = 'Save Changes'
                      editBtn.disabled = true
                      break
                    } else {
                      okBtn.textContent = 'OK'
                      editBtn.disabled = false
                    }
                  }
                }
                else
                {
                  selectedrow.classList.add('selected', 'border', 'border-danger')
                  okBtn.textContent = 'Save Changes'
                  editBtn.disabled = true
                }
              }

              const asyncConfirm = (text) => {
                return new Promise(resolve => {
                  const wrapper = document.querySelector('#popup-box');
                  const editor = document.createElement('div');
                  editor.className = 'modal'
                  wrapper.appendChild(editor)

                  const modalheader = document.createElement('h4')
                  const modalcontent = document.createElement('div')
                  const nodedetails = document.createElement('div')
                  const buttonbar = document.createElement('div')
                  const existingprops = document.createElement('div')
                  existingprops.className = "row col-sm-8 col-md-8 col-lg-8"
                  existingprops.id = 'customprops'
                  modalheader.className='modal-title'
                  modalheader.textContent = ('View node properties')
                  nodedetails.className = 'nodedetails'
                  modalcontent.className='modal-content'
                  buttonbar.className='buttonbar'
                  editor.appendChild(modalcontent)
                  modalcontent.appendChild(modalheader)
                  modalcontent.appendChild(nodedetails)
                  nodedetails.appendChild(existingprops)
                  modalcontent.append(buttonbar)

                  const okBtn = document.createElement('button');
                  const cancelBtn = document.createElement('button');
                  const editBtn = document.createElement('button');
                  okBtn.textContent = 'Ok';
                  okBtn.id = 'okBtn'
                  editBtn.textContent = 'Edit Node'
                  editBtn.id = 'editBtn'
                  cancelBtn.textContent = 'Cancel';


                  for (const [index, [key, value]] of Object.entries(Object.entries(node2editdata))) {
                    if (key == "width" || key == "id" || value == "undefined") {
                      continue
                    }
                    console.log(key, value);
                    const row = document.createElement('div')
                    const col1 = document.createElement('div')
                    const col2 = document.createElement('div')
                    col1.className = 'col-sm-3 col-md-3 col-lg-3'
                    col2.className = 'col-sm-3 col-md-3 col-lg-3'
                    row.className='row'
                    row.id = index
                    existingprops.appendChild(row)
                    const nodename = document.createElement('input');
                    const nodedescription = document.createElement('input');

                    if ( key == "name" ) {
                      nodename.setAttribute('readonly', true)
                    }
                    nodename.setAttribute("name", key)
                    nodename.value = key
                    nodedescription.setAttribute("name", value)
                    nodedescription.setAttribute('readonly', true)

                    nodedescription.value = value
                    row.append(col1)
                    col1.appendChild(nodename)
                    row.append(col2)
                    col2.appendChild(nodedescription)
                  }

                  buttonbar.appendChild(okBtn)
                  buttonbar.appendChild(editBtn)
                  buttonbar.appendChild(cancelBtn)



                  const onClick = pass => {
                    resolve(pass);

                    if (pass != false) {
                      const div2edit = document.querySelector('#customprops')
                      let rows = Array.from(div2edit.getElementsByClassName('row'))
                      let inputs = div2edit.getElementsByTagName('input');
                      var nodename
                      var newpropertyobj = {}

                      rows.forEach(function (row){
                        console.log('row', row)
                        if ( row.classList.contains('selected')) {
                          newpropertyobj[row.childNodes[0].childNodes[0].value] = 'undefined'
                          console.log("miss")
                        }
                        else {
                          if (row.childNodes[0].childNodes[0].value == "active") {
                            newpropertyobj[row.childNodes[0].childNodes[0].value] = (row.childNodes[1].childNodes[0].value==='true')
                          }
                          else if (row.childNodes[0].childNodes[0].value != '') {
                            newpropertyobj[row.childNodes[0].childNodes[0].value] = row.childNodes[1].childNodes[0].value
                          }
                        }
                      })
                    }

                    self.nodedata = newpropertyobj
                    console.log("!!!! ", newpropertyobj)
                    console.log("!!!! ", self.nodedata)
                    editor.remove()

                  };
                  const toggle = (action) => {
                    const modaltitle = document.getElementsByClassName('modal-title')
                    const div2edit = document.querySelector('#customprops')
                    const proprows = div2edit.childNodes
                    const editBtn = document.getElementById('editBtn')
                    let inputs = div2edit.getElementsByTagName('input');
                    let entryArray = Array.from(inputs)

                    if (action == "View"){
                      modaltitle[0].textContent = 'View node properties'
                      entryArray.forEach(function (input) {
                        if (input.name == "name" )
                        {
                          return
                        }
                        input.readOnly = true
                      })

                      proprows.forEach(function ( row, index) {
                        if (row.childNodes[0].childNodes[0].value != 'name') {
                          row.removeEventListener('click', toggleSelect.bind(null, index, '#customprops'))
                          const selectdelete = document.getElementById('selectdelete' + index)
                          selectdelete.parentNode.removeChild(selectdelete)
                        }
                      })
                      const addPropBtn = document.getElementById('addPropBtn')
                      editBtn.textContent = "Edit Node"
                      addPropBtn.parentNode.removeChild(addPropBtn)

                    }

                    if (action == 'Edit Node') {
                      modaltitle[0].textContent = 'Edit node properties'
                      entryArray.forEach(function ( input) {
                        if (input.name == 'name' )
                        {
                          return
                        }
                        input.readOnly = false
                      })
                      proprows.forEach(function ( row, index) {
                        if (row.childNodes[0].childNodes[0].value != 'name') {
                          const selectdelete = document.createElement('span')
                          const col3 = document.createElement('div')
                          const img = document.createElement('img')
                          selectdelete.id = 'selectdelete' + index
                          img.setAttribute("src", "../assets/remove.svg")
                          img.classList.add('selectdeleteimg')
                          selectdelete.addEventListener('click', toggleSelect.bind(null, index, '#customprops'))
                          col3.className = 'col-sm-3 col-md-3 col-lg-3'
                          selectdelete.appendChild(img)
                          row.appendChild(col3)
                          col3.appendChild(selectdelete)
                        }
                      })

                      const addPropBtn = document.createElement('button');
                      addPropBtn.textContent = 'Add Property';
                      addPropBtn.id = "addPropBtn"
                      addPropBtn.addEventListener('click', addProperty)
                      buttonbar.insertBefore(addPropBtn, cancelBtn)
                      editBtn.textContent = 'View'
                    }
                  }

                  okBtn.addEventListener('click', onClick.bind(null, true));
                  editBtn.addEventListener('click', function () {
                    toggle(editBtn.textContent)
                  })
                  cancelBtn.addEventListener('click', onClick.bind(null, false));
                })
              };

              const run = async () => {
                if (await asyncConfirm(node2editdata)) {
                  editNode('💡Item');
                }
              }
              run()

            }
          },
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
              const addItem = () => {
                let pos = event.position || event.cyPosition;
                if (self.nodedata.name != '') {
                  cy.add({
                    group: 'nodes',
                    data: self.nodedata,
                    position: {
                      x: pos.x,
                      y: pos.y
                    },
                  });
                }
              }

              const addProperty = () => {
                const div2append = document.querySelector('div.nodedetails')
                const numrows = div2append.childNodes.length
                const inputdiv = document.createElement('div')
                const row = document.createElement('div')
                const col =  document.createElement('div')
                const col2 =  document.createElement('div')
                inputdiv.className = 'col-sm-8 col-md-8 col-lg-8'
                inputdiv.id = 'customprops'
                row.className = 'row'
                row.id = numrows
                col.className = 'col-sm-3 col-md-3 col-lg-3'
                col2.className = 'col-sm-3 col-md-3 col-lg-3'
                div2append.appendChild(row)

                const propname = document.createElement('input');
                const propvalue = document.createElement('input');
                const labelpropname = document.createElement('label');
                const labelproptext = document.createTextNode("Property name")
                const labelpropvalue = document.createElement('label');
                const labelpropvaltext = document.createTextNode("Property value")
                propname.setAttribute('name', 'propname')
                propvalue.setAttribute('name', 'propvalue')
                propname.setAttribute('id', Date.now().toString())
                propvalue.setAttribute('id', Date.now().toString())
                propname.setAttribute('placeholder', 'Enter the name of your property')
                propvalue.setAttribute('placeholder', 'Enter the value of your property')

                row.appendChild(col)
                col.appendChild(labelpropname)
                col.append(labelproptext)
                col.appendChild(propname)
                row.appendChild(col2)
                propname.focus()
                col2.appendChild(labelpropvalue)
                col2.appendChild(labelpropvaltext)
                col2.appendChild(propvalue)
                const addPropBtn = document.getElementById("addPropBtn")
                addPropBtn.textContent = "Add another"
              }

              const asyncConfirm = (text) => {
                return new Promise(resolve => {
                  const wrapper = document.querySelector('#popup-box');
                  const popup = document.createElement('div');
                  const row = document.createElement('div');
                  const rowcol = document.createElement('div');
                  const col1 = document.createElement('div');
                  const col2 = document.createElement('div');
                  rowcol.className = 'col-sm-3 col-md-6 col-lg-6'
                  row.className = 'row'
                  col1.className = 'col-sm-3 col-md-3 col-lg-3'
                  col2.className = 'col-sm-3 col-md-3 col-lg-3'
                  popup.classList.add('modal');
                  wrapper.appendChild(popup);
                  popup.textContent = text;
                  const modalheader = document.createElement('h4')
                  const modalcontent = document.createElement('div')
                  const nodedetails = document.createElement('div')
                  const buttonbar = document.createElement('div')
                  modalheader.className='modal-title'
                  modalheader.textContent = ('Add a new node')
                  nodedetails.className = 'nodedetails'
                  modalcontent.className='modal-content'
                  buttonbar.className='buttonbar'
                  popup.appendChild(modalcontent)
                  modalcontent.appendChild(modalheader)

                  const nodename = document.createElement('input');
                  const labelnodename = document.createElement('label');
                  const labelnodetext = document.createTextNode("Node name")
                  const nodedescription = document.createElement('input');
                  const labeldescription = document.createElement('label');
                  const labeldesctext = document.createTextNode("Node description")
                  nodename.setAttribute("name", "nodename")
                  labelnodename.setAttribute("for", "nodename")
                  nodedescription.setAttribute("name", "nodedescription")
                  labeldescription.setAttribute("for", "nodedescription")

                  const addPropBtn = document.createElement('button');
                  const okBtn = document.createElement('button');
                  const cancelBtn = document.createElement('button');
                  addPropBtn.id = 'addPropBtn'
                  addPropBtn.textContent = 'Add Property';
                  okBtn.textContent = 'Save Info';
                  cancelBtn.textContent = 'Cancel';

                  modalcontent.appendChild(nodedetails)
                  nodedetails.appendChild(rowcol)
                  rowcol.appendChild(row)
                  row.appendChild(col1)
                  col1.appendChild(labelnodename)
                  col1.appendChild(labelnodetext)
                  col1.appendChild(nodename)
                  col1.appendChild(labelnodename)

                  nodename.focus()
                  row.appendChild(col2)
                  col2.appendChild(labeldescription)
                  col2.appendChild(labeldesctext)
                  col2.appendChild(nodedescription)
                  modalcontent.appendChild(buttonbar)
                  buttonbar.appendChild(okBtn);
                  buttonbar.appendChild(addPropBtn)
                  buttonbar.appendChild(cancelBtn);


                  const onClick = (pass) => {
                    resolve(pass);

                    if (pass != false) {
                      const div2edit = document.querySelector('div.nodedetails')
                      let inputs = div2edit.getElementsByTagName('input');
                      let rows = div2edit.getElementsByClassName('row')
                      var values = {}
                      var itemname
                      var itemvalue
                      let entryArray = Array.from(inputs)

                      for (let i = 0; i < entryArray.length; i++) {
                        if (entryArray[i].name == "nodename") {
                          itemname = 'name'
                          itemvalue = entryArray[i].value

                        } else if (entryArray[i].name == "nodedescription") {
                          itemname = 'nodedescription'
                          itemvalue = entryArray[i].value
                        } else {
                          itemname = entryArray[i].value
                          itemvalue = entryArray[i + 1].value
                          i++
                        }

                        if (itemname != '') {
                          values[itemname] = itemvalue
                        }
                      }
                      values['active'] = false
                      values['width'] = 140
                      self.nodedata = values

                    }

                    popup.remove()

                  };

                  addPropBtn.addEventListener('click', addProperty.bind(null, false));
                  addPropBtn.textContent = 'Add a property'
                  okBtn.addEventListener('click', onClick.bind(null, self.nodedata));
                  cancelBtn.addEventListener('click', onClick.bind(true, false));

                })
              };


              const run = async () => {
                if (await asyncConfirm('Add new node')) {
                  addItem(self.nodedata);
                }
              }
              self.nodedata = {}
              run()

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

        let dataToExport = cy.json()

        Object.entries(dataToExport.elements.nodes).forEach(([key, value]) => {
          Object.entries(value.data).forEach(([k,v]) => {
            if (v == 'undefined') {
              delete(dataToExport.elements.nodes[key].data[k])
            }
          })
        });

        const fixedDataToExport = JSON.stringify(dataToExport, (key, value) => {
          if (!isNaN(value) && value !== "" && typeof value != "boolean")
            value = Number(value)
          return value
        })

        let tzstamp = new Date().toISOString().slice(0, 19).replace(new RegExp(/T|:+/g, "gm"), "-");
        const blob = new Blob([fixedDataToExport], {type: 'application/json charset=utf-8'});
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

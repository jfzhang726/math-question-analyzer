
        console.log("Starting knowledge_graph.js");
        let cytoscape_data = { nodes: [], edges: [] };
        console.log("Concept:", "Proportional Relationships");
        cytoscape_data.nodes.push({ data: { id: 'Proportional Relationships', label: 'Proportional Relationships', type: 'main' } });
    
                cytoscape_data.nodes.push({ data: { id: 'Algebraic Equations', label: 'Algebraic Equations', type: 'related' } });
                cytoscape_data.edges.push({ data: { source: 'Proportional Relationships', target: 'Algebraic Equations', weight: 1 } });
            
                cytoscape_data.nodes.push({ data: { id: 'subtraction', label: 'subtraction', type: 'related' } });
                cytoscape_data.edges.push({ data: { source: 'Proportional Relationships', target: 'subtraction', weight: 1 } });
            
                cytoscape_data.nodes.push({ data: { id: 'Grass Growth Rate', label: 'Grass Growth Rate', type: 'related' } });
                cytoscape_data.edges.push({ data: { source: 'Proportional Relationships', target: 'Grass Growth Rate', weight: 1 } });
            
                cytoscape_data.nodes.push({ data: { id: 'Rate of Work', label: 'Rate of Work', type: 'related' } });
                cytoscape_data.edges.push({ data: { source: 'Proportional Relationships', target: 'Rate of Work', weight: 1 } });
            
                cytoscape_data.nodes.push({ data: { id: 'Knowledge of Proportionality', label: 'Knowledge of Proportionality', type: 'prerequisite' } });
                cytoscape_data.edges.push({ data: { source: 'Proportional Relationships', target: 'Knowledge of Proportionality', weight: 1 } });
            
                cytoscape_data.nodes.push({ data: { id: 'Understanding of Rates and Ratios', label: 'Understanding of Rates and Ratios', type: 'prerequisite' } });
                cytoscape_data.edges.push({ data: { source: 'Proportional Relationships', target: 'Understanding of Rates and Ratios', weight: 1 } });
            
                cytoscape_data.nodes.push({ data: { id: 'Basic Algebra', label: 'Basic Algebra', type: 'prerequisite' } });
                cytoscape_data.edges.push({ data: { source: 'Proportional Relationships', target: 'Basic Algebra', weight: 1 } });
            
        console.log("Cytoscape Data:", cytoscape_data);
        if (cytoscape_data.nodes.length > 0) {
          let cy = cytoscape({
              container: document.getElementById('cy'),
              elements: cytoscape_data,
              style: [
                  {
                      selector: 'node',
                      style: {
                          'background-color': 'data(type) === "main" ? "red" : data(type) === "related" ? "blue" : "green"',
                          'label': 'data(label)'
                      }
                  },
                  {
                      selector: 'edge',
                      style: {
                          'width': 'data(weight)',
                          'line-color': '#888'
                      }
                  }
              ],
              layout: {
                  name: 'cose'
              }
          });
          cy.on('layoutstop', function(){
            console.log('Layout complete!');
          })
        } else {
          console.log("No data to display.");
          document.getElementById('cy').innerText = "No data to display.";
        }
        console.log("Ending knowledge_graph.js");
    
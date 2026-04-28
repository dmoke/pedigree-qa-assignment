const API = "http://127.0.0.1:8000";

let allDogs = [];
const dogMap = new Map(); // id -> dog object for quick lookup

async function getDogs() {
  return fetch(`${API}/dogs`).then(r => r.json());
}

async function getDog(id) {
  return fetch(`${API}/dogs/${id}`).then(r => r.json());
}

async function getAncestors(id) {
  return fetch(`${API}/dogs/${id}/ancestors`).then(r => r.json());
}

let selectedDogId = null;
let currentTree = null;

/* SETUP DRAGGABLE RESIZE */
function setupResize() {
  const handle = document.getElementById("resize-handle");
  const container = document.getElementById("dogs-list-container");
  let isResizing = false;

  handle.addEventListener("mousedown", () => {
    isResizing = true;
    document.body.style.cursor = "row-resize";
  });

  document.addEventListener("mousemove", (e) => {
    if (!isResizing) return;

    const bodyRect = document.body.getBoundingClientRect();
    const newHeight = e.clientY - bodyRect.top - 10;

    if (newHeight > 80 && newHeight < 500) {
      container.style.flex = `0 1 ${newHeight}px`;
    }
  });

  document.addEventListener("mouseup", () => {
    isResizing = false;
    document.body.style.cursor = "default";
  });
}

/* SETUP SEARCH */
function setupSearch() {
  const searchInput = document.getElementById("search-input");
  const searchClear = document.getElementById("search-clear");

  const filterDogs = () => {
    const query = searchInput.value.toLowerCase().trim();

    if (query === "") {
      // Show all dogs
      document.querySelectorAll(".dog-list-card").forEach(card => {
        card.style.display = "";
      });
      return;
    }

    // Filter dogs
    document.querySelectorAll(".dog-list-card").forEach(card => {
      const dogId = card.dataset.id;
      const dog = dogMap.get(dogId);

      if (!dog) return;

      const matchesId = dogId.includes(query);
      const matchesName = dog.name.toLowerCase().includes(query);

      card.style.display = (matchesId || matchesName) ? "" : "none";
    });
  };

  searchInput.addEventListener("input", filterDogs);

  // Clear button
  searchClear.addEventListener("click", () => {
    searchInput.value = "";
    filterDogs();
    searchInput.focus();
  });

  // Prevent form submission if Enter is pressed
  searchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
    }
  });
}

async function init() {
  try {
    setupResize();
    setupSearch();

    allDogs = await getDogs();
    allDogs.forEach(dog => {
      dogMap.set(dog.id, dog);
    });

    const list = document.getElementById("dogs-list");
    list.innerHTML = "";

    allDogs.forEach(dog => {
      const card = document.createElement("div");
      card.className = "dog-list-card";
      card.dataset.id = dog.id;

      card.innerHTML = `
        <div class="dog-list-card__id">#${dog.id}</div>
        <img src="favicon.ico" class="dog-list-card__icon" alt="dog" />
        <div class="dog-list-card__name">${dog.name}</div>
      `;

      card.onclick = () => selectDog(dog.id);
      list.appendChild(card);
    });
  } catch (error) {
    console.error("Error loading dogs:", error);
  }
}

async function selectDog(id) {
  try {
    selectedDogId = id;

    // Update active card styling
    document.querySelectorAll(".dog-list-card").forEach(card => {
      card.classList.remove("active");
    });
    document.querySelector(`[data-id="${id}"]`)?.classList.add("active");

    // Load dog and ancestors
    const dog = await getDog(id);
    const ancestorsData = await getAncestors(id);

    renderDogCard(dog);
    renderFamilyTree(dog, ancestorsData.ancestors);
  } catch (error) {
    console.error("Error selecting dog:", error);
    document.getElementById("left-panel").innerHTML = `<div class="no-data">Error loading dog info</div>`;
    document.getElementById("right-panel").innerHTML = `<div class="no-data">Error loading family tree</div>`;
  }
}

async function peekDog(dogId, allAncestors, rootDog) {
  try {
    const dog = await getDog(dogId);
    const panel = document.getElementById("left-panel");

    const heightStr = dog.height_cm !== null ? `${dog.height_cm} cm` : "—";
    const weightStr = dog.weight_kg !== null ? `${dog.weight_kg} kg` : "—";

    // Get parent names
    let sireDisplay = "—";
    let damDisplay = "—";

    if (dog.sire_id) {
      const sire = dogMap.get(dog.sire_id);
      const sireName = sire ? sire.name : "?";
      sireDisplay = `<span class="parent-id" data-dog-id="${dog.sire_id}">#${dog.sire_id} (${sireName})</span>`;
    }

    if (dog.dam_id) {
      const dam = dogMap.get(dog.dam_id);
      const damName = dam ? dam.name : "?";
      damDisplay = `<span class="parent-id" data-dog-id="${dog.dam_id}">#${dog.dam_id} (${damName})</span>`;
    }

    // Get children (dogs for which this dog is a parent) - only from dogs visible in current tree
    let childrenDisplay = "—";
    const childrenSet = new Set();

    // Build a list of all dogs visible in the tree (ancestors + root)
    const dogsInTree = [rootDog, ...allAncestors];

    // Find children: dogs in the tree whose parent is this dog
    dogsInTree.forEach(a => {
      if ((a.sire_id === dogId || a.dam_id === dogId)) {
        childrenSet.add(a.id);
      }
    });

    if (childrenSet.size > 0) {
      const childrenArray = Array.from(childrenSet).map(childId => {
        // Find child in the current tree
        const child = dogsInTree.find(a => a.id === childId);
        return child ? `<span class="child-id" data-dog-id="${child.id}">#${child.id} (${child.name})</span>` : "";
      }).filter(x => x !== "");
      childrenDisplay = childrenArray.join(", ");
    }

    panel.innerHTML = `
      <div class="dog-card peek">
        <div class="dog-card__header">
          <img src="favicon.ico" class="dog-card__icon" alt="dog" />
          <div class="dog-card__id">#${dog.id}</div>
          <div class="dog-card__name">${dog.name} <span class="peek-indicator">PEEK</span></div>
        </div>
        <div class="dog-card__field">
          <span class="dog-card__label">Breed:</span>
          <span class="dog-card__value">${dog.breed}</span>
        </div>
        <div class="dog-card__field">
          <span class="dog-card__label">Sex:</span>
          <span class="dog-card__value">${dog.sex}</span>
        </div>
        <div class="dog-card__field">
          <span class="dog-card__label">Height:</span>
          <span class="dog-card__value">${heightStr}</span>
        </div>
        <div class="dog-card__field">
          <span class="dog-card__label">Weight:</span>
          <span class="dog-card__value">${weightStr}</span>
        </div>
        <div class="dog-card__field">
          <span class="dog-card__label">Sire:</span>
          <span class="dog-card__value">${sireDisplay}</span>
        </div>
        <div class="dog-card__field">
          <span class="dog-card__label">Dam:</span>
          <span class="dog-card__value">${damDisplay}</span>
        </div>
        <div class="dog-card__field">
          <span class="dog-card__label">Children:</span>
          <span class="dog-card__value">${childrenDisplay}</span>
        </div>
      </div>
    `;

    // Add click handlers to parent and child IDs
    document.querySelectorAll(".parent-id, .child-id").forEach(link => {
      link.addEventListener("click", (e) => {
        e.stopPropagation();
        const dogId = link.dataset.dogId;
        selectDog(dogId);
      });
    });
  } catch (error) {
    console.error("Error peeking dog:", error);
  }
}

function renderDogCard(dog) {
  const panel = document.getElementById("left-panel");

  if (!dog) {
    panel.innerHTML = `<div class="no-data">No dog selected</div>`;
    return;
  }

  const heightStr = dog.height_cm !== null ? `${dog.height_cm} cm` : "—";
  const weightStr = dog.weight_kg !== null ? `${dog.weight_kg} kg` : "—";

  // Get parent names
  let sireDisplay = "—";
  let damDisplay = "—";

  if (dog.sire_id) {
    const sire = dogMap.get(dog.sire_id);
    const sireName = sire ? sire.name : "?";
    sireDisplay = `<span class="parent-id" data-dog-id="${dog.sire_id}">#${dog.sire_id} (${sireName})</span>`;
  }

  if (dog.dam_id) {
    const dam = dogMap.get(dog.dam_id);
    const damName = dam ? dam.name : "?";
    damDisplay = `<span class="parent-id" data-dog-id="${dog.dam_id}">#${dog.dam_id} (${damName})</span>`;
  }

  panel.innerHTML = `
    <div class="dog-card">
      <div class="dog-card__header">
        <img src="favicon.ico" class="dog-card__icon" alt="dog" />
        <div class="dog-card__id">#${dog.id}</div>
        <div class="dog-card__name">${dog.name}</div>
      </div>
      <div class="dog-card__field">
        <span class="dog-card__label">Breed:</span>
        <span class="dog-card__value">${dog.breed}</span>
      </div>
      <div class="dog-card__field">
        <span class="dog-card__label">Sex:</span>
        <span class="dog-card__value">${dog.sex}</span>
      </div>
      <div class="dog-card__field">
        <span class="dog-card__label">Height:</span>
        <span class="dog-card__value">${heightStr}</span>
      </div>
      <div class="dog-card__field">
        <span class="dog-card__label">Weight:</span>
        <span class="dog-card__value">${weightStr}</span>
      </div>
      <div class="dog-card__field">
        <span class="dog-card__label">Sire:</span>
        <span class="dog-card__value">${sireDisplay}</span>
      </div>
      <div class="dog-card__field">
        <span class="dog-card__label">Dam:</span>
        <span class="dog-card__value">${damDisplay}</span>
      </div>
    </div>
  `;

  // Add click handlers to parent ID links (to select them)
  document.querySelectorAll(".parent-id").forEach(link => {
    link.addEventListener("click", (e) => {
      e.stopPropagation();
      const dogId = link.dataset.dogId;
      selectDog(dogId);
    });
  });
}

function renderFamilyTree(rootDog, ancestors) {
  const panel = document.getElementById("right-panel");

  if (!rootDog) {
    panel.innerHTML = `<div class="no-data">No dog selected</div>`;
    return;
  }

  if (ancestors.length === 0) {
    panel.innerHTML = `<div id="tree-container"><div class="no-data">No ancestors found for this dog</div></div>`;
    return;
  }

  // Build ancestor tree by generation
  const ancestorsByGeneration = {};
  const visited = new Set();

  function addAncestor(dog, generation) {
    if (visited.has(dog.id)) return;
    visited.add(dog.id);

    if (!ancestorsByGeneration[generation]) {
      ancestorsByGeneration[generation] = [];
    }
    ancestorsByGeneration[generation].push(dog);
  }

  // Start with direct parents (generation 1)
  if (rootDog.sire_id) {
    const sire = ancestors.find(a => a.id === rootDog.sire_id);
    if (sire) addAncestor(sire, 1);
  }
  if (rootDog.dam_id) {
    const dam = ancestors.find(a => a.id === rootDog.dam_id);
    if (dam) addAncestor(dam, 1);
  }

  // Add subsequent generations
  for (let gen = 1; gen < 10; gen++) {
    if (!ancestorsByGeneration[gen]) break;

    ancestorsByGeneration[gen].forEach(dog => {
      if (dog.sire_id) {
        const sire = ancestors.find(a => a.id === dog.sire_id);
        if (sire) addAncestor(sire, gen + 1);
      }
      if (dog.dam_id) {
        const dam = ancestors.find(a => a.id === dog.dam_id);
        if (dam) addAncestor(dam, gen + 1);
      }
    });
  }

  // Render tree top to bottom (but reversed in CSS to show root at bottom)
  let html = `<div id="tree-container"><svg id="tree-svg"></svg><div class="tree">`;

  // Root dog
  html += `
    <div class="tree-level">
      <div class="tree-node root" data-node-id="${rootDog.id}">
        <div class="tree-node__id">#${rootDog.id}</div>
        <div class="tree-node__name">${rootDog.name}</div>
        <div class="tree-node__breed">${rootDog.breed}</div>
      </div>
    </div>
  `;

  // Ancestor generations
  for (let gen = 1; gen <= 10; gen++) {
    if (!ancestorsByGeneration[gen] || ancestorsByGeneration[gen].length === 0) break;

    html += `<div class="tree-level">`;
    ancestorsByGeneration[gen].forEach(dog => {
      html += `
        <div class="tree-node" data-node-id="${dog.id}">
          <div class="tree-node__id">#${dog.id}</div>
          <div class="tree-node__name">${dog.name}</div>
          <div class="tree-node__breed">${dog.breed}</div>
        </div>
      `;
    });
    html += `</div>`;
  }

  html += `</div></div>`;
  panel.innerHTML = html;

  // Post-processing: Nudge parents up visually if on same row as children
  document.querySelectorAll(".tree-level").forEach(level => {
    const nodes = Array.from(level.querySelectorAll(".tree-node"));

    nodes.forEach(parentNode => {
      const parentDogId = parentNode.dataset.nodeId;
      const parentDog = ancestors.find(a => a.id === parentDogId) || (parentDogId === rootDog.id ? rootDog : null);

      if (!parentDog) return;

      // Check if any node in this same row is a child of this parent
      const hasChildInRow = nodes.some(node => {
        const childDog = ancestors.find(a => a.id === node.dataset.nodeId) || (node.dataset.nodeId === rootDog.id ? rootDog : null);
        return childDog && (childDog.sire_id === parentDogId || childDog.dam_id === parentDogId);
      });

      // If parent has child on same row, nudge parent up halfway
      if (hasChildInRow) {
        parentNode.style.transform = "translateY(-25px)";
      }
    });
  });

  // Store current selected dog for restoration on hover leave
  const selectedDog = rootDog;

  // Add click and hover handlers to tree nodes
  document.querySelectorAll(".tree-node:not(.root)").forEach(node => {
    node.addEventListener("click", (e) => {
      e.stopPropagation();
      const dogId = node.dataset.nodeId;
      selectDog(dogId);
    });

    // Hover: peek at this dog and highlight parent lines
    node.addEventListener("mouseenter", (e) => {
      const dogId = node.dataset.nodeId;
      peekDog(dogId, ancestors, rootDog);

      // Fade all lines and highlight only connected ones
      const nodeRect = node.getBoundingClientRect();
      const containerRect = document.getElementById("tree-container").getBoundingClientRect();
      const nodeX = nodeRect.left - containerRect.left + nodeRect.width / 2;
      const nodeY = nodeRect.top - containerRect.top + nodeRect.height / 2;

      document.querySelectorAll("svg line").forEach(line => {
        line.classList.add("faded");
        line.classList.remove("highlight");

        const x1 = parseFloat(line.getAttribute("x1"));
        const y1 = parseFloat(line.getAttribute("y1"));
        const x2 = parseFloat(line.getAttribute("x2"));
        const y2 = parseFloat(line.getAttribute("y2"));

        const tolerance = 5;
        if (
          (Math.abs(x2 - nodeX) < tolerance && Math.abs(y2 - nodeY) < tolerance) ||
          (Math.abs(x1 - nodeX) < tolerance && Math.abs(y1 - nodeY) < tolerance)
        ) {
          line.classList.remove("faded");
          line.classList.add("highlight");
        }
      });
    });

    // Leave: restore selected dog card and remove line highlights
    node.addEventListener("mouseleave", (e) => {
      renderDogCard(selectedDog);
      document.querySelectorAll("svg line").forEach(line => {
        line.classList.remove("faded");
        line.classList.remove("highlight");
      });
    });
  });

  // Draw connection lines after DOM is ready
  requestAnimationFrame(() => {
    drawConnectionLines(rootDog, ancestors, ancestorsByGeneration);
  });
}

function drawConnectionLines(rootDog, ancestors, ancestorsByGeneration) {
  const svg = document.getElementById("tree-svg");
  const treeContainer = document.getElementById("tree-container");

  if (!svg || !treeContainer) return;

  // Create a map of nodes with generation info
  const nodeMap = new Map();
  const nodeGenMap = new Map();

  document.querySelectorAll(".tree-node").forEach(node => {
    nodeMap.set(node.dataset.nodeId, node);
  });

  // Mark which generation each node is in
  nodeGenMap.set(rootDog.id, 0); // Root is generation 0

  for (let gen = 1; gen <= 10; gen++) {
    if (ancestorsByGeneration[gen]) {
      ancestorsByGeneration[gen].forEach(dog => {
        nodeGenMap.set(dog.id, gen);
      });
    }
  }

  // Function to get center of a node
  const getNodeCenter = (nodeEl) => {
    const rect = nodeEl.getBoundingClientRect();
    const containerRect = treeContainer.getBoundingClientRect();
    return {
      x: rect.left - containerRect.left + rect.width / 2,
      y: rect.top - containerRect.top + rect.height / 2
    };
  };

  // Color palette for different generations (distance from root)
  const generationColors = [
    "#2196F3", // Gen 0 (root) - Blue
    "#4CAF50", // Gen 1 - Green
    "#FF9800", // Gen 2 - Orange
    "#F44336", // Gen 3 - Red
    "#9C27B0", // Gen 4 - Purple
    "#00BCD4"  // Gen 5 - Cyan
  ];

  // For root dog, draw lines from its parents (sire and dam)
  if (rootDog.sire_id) {
    const sireNode = nodeMap.get(rootDog.sire_id);
    const rootNode = nodeMap.get(rootDog.id);
    if (sireNode && rootNode) {
      const sireCenter = getNodeCenter(sireNode);
      const rootCenter = getNodeCenter(rootNode);
      const sirGen = nodeGenMap.get(rootDog.sire_id) || 1;
      drawLine(svg, sireCenter, rootCenter, sirGen);
    }
  }

  if (rootDog.dam_id) {
    const damNode = nodeMap.get(rootDog.dam_id);
    const rootNode = nodeMap.get(rootDog.id);
    if (damNode && rootNode) {
      const damCenter = getNodeCenter(damNode);
      const rootCenter = getNodeCenter(rootNode);
      const damGen = nodeGenMap.get(rootDog.dam_id) || 1;
      drawLine(svg, damCenter, rootCenter, damGen);
    }
  }

  // For each ancestor, draw lines to its children (both ancestors and root)
  for (let gen = 1; gen <= 10; gen++) {
    if (!ancestorsByGeneration[gen]) break;

    ancestorsByGeneration[gen].forEach(ancestor => {
      const ancestorNode = nodeMap.get(ancestor.id);
      if (!ancestorNode) return;
      const ancestorCenter = getNodeCenter(ancestorNode);
      const ancestorGen = nodeGenMap.get(ancestor.id) || gen;

      // Find direct children in ancestors list
      ancestors.forEach(dog => {
        if (dog.sire_id === ancestor.id || dog.dam_id === ancestor.id) {
          const childNode = nodeMap.get(dog.id);
          if (childNode) {
            const childCenter = getNodeCenter(childNode);
            drawLine(svg, ancestorCenter, childCenter, ancestorGen);
          }
        }
      });
    });
  }
}

function drawLine(svg, from, to, generation = 0) {
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");

  line.setAttribute("x1", from.x);
  line.setAttribute("y1", from.y);
  line.setAttribute("x2", to.x);
  line.setAttribute("y2", to.y);

  // Color based on generation distance from root
  const generationColors = [
    "#2196F3", // Gen 0 - Blue
    "#4CAF50", // Gen 1 - Green
    "#FF9800", // Gen 2 - Orange
    "#F44336", // Gen 3 - Red
    "#9C27B0", // Gen 4 - Purple
    "#00BCD4"  // Gen 5 - Cyan
  ];

  const color = generationColors[generation % generationColors.length] || "#999";

  line.setAttribute("stroke", color);
  line.setAttribute("stroke-width", "2.5");
  line.setAttribute("opacity", "0.8");
  line.setAttribute("class", "parent-line");
  line.setAttribute("data-generation", generation);

  svg.appendChild(line);
}

init();

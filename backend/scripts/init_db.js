// MongoDB initialization script for Emergent Storyboard (StoryCanvas)
// Usage (Windows PowerShell):
//   mongosh "${env:MONGO_URL:-mongodb://localhost:27017}" backend/scripts/init_db.js
// Or explicitly:
//   mongosh "mongodb://localhost:27017" backend/scripts/init_db.js

(function () {
  const dbName = (process.env && (process.env.DB_NAME || process.env.npm_config_DB_NAME)) || 'Storyboard';
  const db = db.getSiblingDB(dbName);

  print(`\n===> Initializing database: ${dbName}`);

  // Helper to create index safely
  function ensureIndex(collection, keys, options) {
    try {
      db[collection].createIndex(keys, options || {});
      print(`✓ Index created on ${collection}: ` + JSON.stringify(keys) + (options ? ' ' + JSON.stringify(options) : ''));
    } catch (e) {
      print(`! Failed to create index on ${collection}: ${e.message}`);
    }
  }

  // Create collections explicitly (no-op if they already exist)
  const collections = [
    'projects',
    'scenes',
    'clips',
    'characters',
    'style_templates',
    'comfyui_servers',
    'generation_batches',
  ];
  collections.forEach((name) => {
    try {
      if (!db.getCollectionNames().includes(name)) {
        db.createCollection(name);
        print(`✓ Collection created: ${name}`);
      } else {
        print(`• Collection exists: ${name}`);
      }
    } catch (e) {
      print(`! Failed to create collection ${name}: ${e.message}`);
    }
  });

  // Indexes
  // projects
  ensureIndex('projects', { id: 1 }, { unique: true });
  ensureIndex('projects', { created_at: -1 });

  // scenes
  ensureIndex('scenes', { id: 1 }, { unique: true });
  ensureIndex('scenes', { project_id: 1, order: 1 });
  ensureIndex('scenes', { parent_scene_id: 1 });
  ensureIndex('scenes', { is_alternate: 1 });

  // clips
  ensureIndex('clips', { id: 1 }, { unique: true });
  ensureIndex('clips', { scene_id: 1, order: 1 });
  ensureIndex('clips', { scene_id: 1, timeline_position: 1 });

  // characters
  ensureIndex('characters', { id: 1 }, { unique: true });
  ensureIndex('characters', { project_id: 1, name: 1 });

  // style templates
  ensureIndex('style_templates', { id: 1 }, { unique: true });
  ensureIndex('style_templates', { project_id: 1, name: 1 });

  // comfyui servers
  ensureIndex('comfyui_servers', { id: 1 }, { unique: true });
  ensureIndex('comfyui_servers', { url: 1 }, { unique: true });

  // generation batches
  ensureIndex('generation_batches', { id: 1 }, { unique: true });
  ensureIndex('generation_batches', { project_id: 1, created_at: -1 });

  print(`\n===> Initialization complete`);
})();

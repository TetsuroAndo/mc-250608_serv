# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Forge-based Minecraft 1.20.1 server focused on modded gameplay with emphasis on weapons, industrial automation, and adventure content. The core feature is the TACZ (Timeless and Classics Guns) mod system providing FPS-style weapon mechanics within Minecraft.

## Server Deployment

### Docker Commands
```bash
# Start the server
docker-compose up -d

# View server logs
docker-compose logs -f mc

# Stop the server
docker-compose down
```

The server runs in Docker with 8GB RAM allocation and optimized JVM settings for performance.

## TACZ Gun System Architecture

### Gun Pack Structure
The server includes 4 major gun packs located in `/server/tacz/`:

- **tacz_default_gun**: Core 40+ weapons with full animations and multi-language support
- **elitex_quality_guns**: 17 premium weapons including CoD Zombies-style wonder weapons
- **lradd_default_gun**: Additional modern weapons with dual namespace system
- **gucci_vuitton_attachment**: 50+ weapon attachments (grips, scopes, muzzles, stocks)

### Gun Pack Components
Each pack contains:
- `assets/`: 3D models, textures, animations (.gltf/.animation.json), sounds
- `data/`: Weapon statistics, crafting recipes, attachment compatibility tags
- `gunpack.meta.json`: Pack metadata and versioning

### Development Mode
Enable debug mode in `/server/tacz/tacz-pre.toml`:
```toml
DefaultPackDebug = true
```
This allows hot-reloading of gun data without server restart.

### Backup System
Automatic timestamped backups are stored in `/server/tacz_backup/` for all gun packs, enabling configuration rollback.

## Configuration Files

### TACZ Settings (`/client/config/tacz-client.toml`)
Key configurations:
- Gun sound range: 64 blocks (16 for silenced)
- Explosive ammo block destruction: enabled
- LOD system for performance optimization
- Bullet hole particle effects

### Server Config (`/client/config/tacz-server.toml`)
- Hitbox latency compensation
- Ammo consumption in creative mode
- Server-side performance settings

## Common Development Tasks

### Weapon Customization
1. Locate weapon data files in `data/{namespace}/data/guns/`
2. Modify JSON files for damage, range, accuracy, etc.
3. Test changes with debug mode enabled
4. Update recipes in `recipes/gun/` if needed

### Attachment Management
1. Define attachments in `gucci_vuitton_attachment/data/`
2. Set compatibility via `tacz_tags/attachments/`
3. Create display models in `display/attachments/`

### Audio/Visual Updates
1. Replace sound files in `tacz_sounds/` directories
2. Update textures in `textures/` subdirectories
3. Modify animations in `animations/` folder (.animation.json or .gltf)

## Mod Integration

### Key Dependencies
- **Create Mod**: Industrial automation integrated with TACZ via `createtaczauto`
- **JEI**: Recipe viewing for custom weapon crafting
- **Iron's Spellbooks**: Magic system alongside gun mechanics
- **Twilight Forest/Alex's Caves**: Adventure content requiring balanced weaponry

### Performance Considerations
The server uses G1GC optimization and 8GB RAM allocation. TACZ LOD system reduces rendering load for distant weapons. Particle effects are time-limited (400 ticks) to prevent lag.

## File Structure Notes

- `/server/mods/`: Contains all .jar mod files
- `/server/tacz/`: Gun pack configurations and assets
- `/client/`: Client-side configs and world data
- `/server/tacz_backup/`: Automated configuration backups
- `docker-compose.yaml`: Server deployment configuration with JVM optimization
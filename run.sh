#!/bin/bash

# スクリプトの設定
SCRIPT_NAME="$(basename "$0")"

# ヘルプメッセージ
show_help() {
  echo "Usage: $SCRIPT_NAME [command]"
  echo "Available commands:"
  echo "  up       - Start the server"
  echo "  down     - Stop the server"
  echo "  restart  - Restart the server"
  echo "  ps       - List running containers"
  echo "  logs     - View server logs"
  echo "  log      - View server logs with error filtering"
  echo "  rcon     - Connect to the server via RCON"
  echo "  reset    - Reset the server (remove all data)"
  echo "  help     - Show this help message"
}

# コマンドの実行
case "$1" in
  up)
    sudo docker compose up -d
    ;;
  down)
    sudo docker compose down
    ;;
  restart)
    sudo docker compose restart
    ;;
  ps)
    sudo docker ps
    ;;
  logs)
    sudo docker compose logs -f mc
    ;;
  log)
    sudo docker compose logs -f mc | grep -i "error\|exception\|warn\|fail"
    ;;
  reset)
    cd server && \
    rm -rf .* *.json crash-reports defaultconfigs *.txt libraries log* run.* tacz_backup user_jvm_args.txt user*
    ;;
  rcon)
    sudo docker exec -it forge-mc rcon-cli
    ;;
  help)
    show_help
    ;;
  *)
    echo "Invalid command. See '$SCRIPT_NAME help' for usage."
    exit 1
    ;;
esac

exit 0

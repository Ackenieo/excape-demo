const {
  palette,
  drawRoundedRect,
  drawCircularAvatar,
  drawButton,
  isPointInRect,
} = require('../../core/ui');

function createGameScene(app) {
  const buttons = [];
  const MAX_DRAFT_LENGTH = 40;
  const CHAT_BOTTOM_GAP = 104;
  const CHAT_SIDE_GAP = 16;
  const CHAT_PADDING_TOP = 18;
  const CHAT_PADDING_BOTTOM = 20;
  const touchState = {
    startPoint: null,
    draggingChat: false,
    moved: false,
    startScrollOffset: 0,
  };
  const scrollState = {
    offset: 0,
    maxOffset: 0,
    chatRect: null,
    lastRunId: '',
    lastMessageCount: 0,
    wasNearBottom: true,
  };

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function buildMessageLines(ctx, text, maxWidth) {
    const chars = String(text || '').split('');
    const lines = [];
    let currentLine = '';

    chars.forEach((char) => {
      const testLine = currentLine + char;
      if (ctx.measureText(testLine).width > maxWidth && currentLine) {
        lines.push(currentLine);
        currentLine = char;
        return;
      }

      currentLine = testLine;
    });

    if (currentLine) {
      lines.push(currentLine);
    }

    return lines;
  }

  function getChatRect(width, height) {
    const systemInfo = app.appStore.systemInfo || {};
    const safeArea = systemInfo.safeArea;
    const safeTop = safeArea && typeof safeArea.top === 'number' ? safeArea.top : 0;
    const statusBarHeight = typeof systemInfo.statusBarHeight === 'number'
      ? systemInfo.statusBarHeight
      : 0;
    const topInset = Math.max(safeTop, statusBarHeight, 24) + 12;
    const navHeight = topInset + 44;
    const meterHeight = 30;

    return {
      x: 0,
      y: navHeight + meterHeight,
      width,
      height: Math.max(0, height - navHeight - meterHeight - CHAT_BOTTOM_GAP),
    };
  }

  function layoutMessages(ctx, run, width) {
    let cursorY = CHAT_PADDING_TOP;
    const avatarSize = 30;
    const avatarGap = 8;
    const bubbleMaxWidth = width * 0.58;

    return run.messages.map((message) => {
      const isMe = message.role === 'player';
      ctx.font = '13px sans-serif';
      const lines = buildMessageLines(ctx, message.content, bubbleMaxWidth - 20);
      const lineWidths = lines.map((line) => ctx.measureText(line).width);
      const widestLine = lineWidths.length ? Math.max.apply(null, lineWidths) : 0;
      const bubbleHeight = lines.length * 18 + 16;
      const bubbleWidth = Math.max(64, Math.min(bubbleMaxWidth, widestLine + 24));
      const titleHeight = isMe ? 0 : 14;
      const avatarX = isMe
        ? width - CHAT_SIDE_GAP - avatarSize
        : CHAT_SIDE_GAP;
      const bubbleX = isMe
        ? avatarX - avatarGap - bubbleWidth
        : avatarX + avatarSize + avatarGap;
      const itemTop = cursorY;
      const avatarY = cursorY;
      const bubbleY = cursorY + titleHeight;
      const itemBottom = Math.max(avatarY + avatarSize, bubbleY + bubbleHeight);

      const item = {
        message,
        isMe,
        lines,
        avatarX,
        avatarY,
        avatarSize,
        bubbleX,
        bubbleY,
        bubbleWidth,
        bubbleHeight,
        titleY: cursorY + 11,
      };

      cursorY = itemBottom + 16;
      item.itemHeight = cursorY - itemTop;
      return item;
    });
  }

  function getTurnsBadgeStyle(run) {
    const maxTurns = run.level && typeof run.level.maxTurns === 'number' && run.level.maxTurns > 0
      ? run.level.maxTurns
      : 5;
    const remainingRatio = clamp(run.remainingTurns / maxTurns, 0, 1);

    if (remainingRatio >= 0.8) {
      return {
        fill: palette.successBg,
        text: palette.successIcon,
      };
    }

    if (remainingRatio >= 0.4) {
      return {
        fill: palette.warningBg,
        text: palette.warningIcon,
      };
    }

    return {
      fill: palette.dangerBg,
      text: palette.danger,
    };
  }

  return {
    render({ ctx, width, height }) {
      buttons.length = 0;
      const run = app.runStore.currentRun;
      const systemInfo = app.appStore.systemInfo || {};
      const safeArea = systemInfo.safeArea;
      const safeTop = safeArea && typeof safeArea.top === 'number' ? safeArea.top : 0;
      const statusBarHeight = typeof systemInfo.statusBarHeight === 'number'
        ? systemInfo.statusBarHeight
        : 0;
      const topInset = Math.max(safeTop, statusBarHeight, 24) + 12;
      const navHeight = topInset + 44;
      const navTextY = topInset + 18;
      const navBadgeY = topInset + 4;
      const meterTop = navHeight;
      const meterTextY = meterTop + 20;
      const meterBarY = meterTop + 13;

      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';

      ctx.fillStyle = palette.bgSecondary;
      ctx.fillRect(0, 0, width, height);

      if (!run) {
        return;
      }

      // Nav Bar
      ctx.fillStyle = palette.bg;
      ctx.fillRect(0, 0, width, navHeight);

      const backButton = {
        x: 10, y: topInset - 6, width: 60, height: 30, action: 'back'
      };
      buttons.push(backButton);

      ctx.fillStyle = palette.primary;
      ctx.font = '14px sans-serif';
      ctx.fillText('< 返回', 20, navTextY);

      // Turns badge
      const badgeWidth = 68;
      const badgeX = (width - badgeWidth) / 2;
      const turnsBadgeStyle = getTurnsBadgeStyle(run);
      ctx.fillStyle = turnsBadgeStyle.fill;
      ctx.beginPath();
      ctx.roundRect(badgeX, navBadgeY, badgeWidth, 22, 11);
      ctx.fill();
      ctx.fillStyle = turnsBadgeStyle.text;
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`剩 ${run.remainingTurns} 句`, badgeX + badgeWidth / 2, navBadgeY + 11);
      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';

      // Meter Bar
      ctx.fillStyle = palette.bg;
      ctx.fillRect(0, meterTop, width, 30);
      ctx.fillStyle = palette.textSub;
      ctx.font = '11px sans-serif';
      ctx.fillText('动摇程度', 20, meterTextY);

      const meterW = width - 120;
      ctx.fillStyle = palette.bgSecondary;
      ctx.beginPath();
      ctx.roundRect(80, meterBarY, meterW, 6, 3);
      ctx.fill();

      ctx.fillStyle = palette.primary;
      ctx.beginPath();
      ctx.roundRect(80, meterBarY, meterW * (run.shakeValue / 100), 6, 3);
      ctx.fill();

      ctx.font = 'bold 11px sans-serif';
      ctx.fillText(`${run.shakeValue}%`, width - 35, meterTextY);

      // Chat area
      const chatRect = getChatRect(width, height);
      scrollState.chatRect = chatRect;
      const items = layoutMessages(ctx, run, width);
      const contentHeight = items.reduce((sum, item) => sum + item.itemHeight, 0) + CHAT_PADDING_BOTTOM;
      scrollState.maxOffset = Math.max(0, contentHeight - chatRect.height);
      const userAvatarImage = app.getImageAsset(app.getUserAvatarSource());
      const npcAvatarImage = app.getImageAsset(
        app.resolveNpcAvatarSource(run.level, run.shakeValue)
      );

      if (scrollState.lastRunId !== run.runId) {
        scrollState.offset = scrollState.maxOffset;
      } else if (scrollState.lastMessageCount !== run.messages.length && scrollState.wasNearBottom) {
        scrollState.offset = scrollState.maxOffset;
      } else {
        scrollState.offset = clamp(scrollState.offset, 0, scrollState.maxOffset);
      }

      scrollState.lastRunId = run.runId;
      scrollState.lastMessageCount = run.messages.length;

      ctx.save();
      ctx.beginPath();
      ctx.rect(chatRect.x, chatRect.y, chatRect.width, chatRect.height);
      ctx.clip();

      const baseY = chatRect.y - scrollState.offset;

      items.forEach((item) => {
        const bubbleTop = baseY + item.bubbleY;
        const itemBottom = bubbleTop + item.bubbleHeight;
        if (itemBottom < chatRect.y - 24 || bubbleTop > chatRect.y + chatRect.height + 24) {
          return;
        }

        if (!item.isMe) {
          ctx.fillStyle = palette.textSub;
          ctx.font = '10px sans-serif';
          ctx.fillText(run.level.name, item.bubbleX, baseY + item.titleY);
        }

        drawCircularAvatar(
          ctx,
          item.isMe ? userAvatarImage : npcAvatarImage,
          item.avatarX,
          baseY + item.avatarY,
          item.avatarSize,
          {
            fallbackText: item.isMe ? '我' : String(run.level.name || 'N').slice(0, 1),
            fallbackFill: item.isMe ? palette.primaryLight : palette.grayBg,
            textColor: item.isMe ? palette.primaryText : palette.textMain,
          }
        );

        drawRoundedRect(
          ctx,
          item.bubbleX,
          bubbleTop,
          item.bubbleWidth,
          item.bubbleHeight,
          10,
          item.isMe ? palette.primary : palette.bgSecondary,
          item.isMe ? null : palette.borderLight,
        );

        item.lines.forEach((line, index) => {
          ctx.fillStyle = item.isMe ? palette.bg : palette.textMain;
          ctx.font = '13px sans-serif';
          ctx.fillText(line, item.bubbleX + 12, bubbleTop + 20 + index * 18);
        });
      });

      ctx.restore();

      if (scrollState.maxOffset > 0) {
        const thumbHeight = Math.max(24, (chatRect.height / contentHeight) * chatRect.height);
        const thumbY = chatRect.y + (scrollState.offset / scrollState.maxOffset) * (chatRect.height - thumbHeight);
        drawRoundedRect(ctx, width - 6, thumbY, 3, thumbHeight, 2, palette.border, null);
      }

      scrollState.wasNearBottom = scrollState.maxOffset - scrollState.offset <= 24;

      // Input dock
      ctx.fillStyle = palette.bg;
      ctx.fillRect(0, height - 92, width, 92);

      ctx.beginPath();
      ctx.moveTo(0, height - 92);
      ctx.lineTo(width, height - 92);
      ctx.strokeStyle = palette.borderLight;
      ctx.lineWidth = 1;
      ctx.stroke();

      const draftText = app.runStore.inputDraft || '';
      const isInputActive = app.runStore.keyboardVisible;
      const inputBox = {
        x: 16,
        y: height - 76,
        width: width - 118,
        height: 44,
        action: 'input',
      };
      buttons.push(inputBox);

      drawRoundedRect(
        ctx,
        inputBox.x,
        inputBox.y,
        inputBox.width,
        inputBox.height,
        22,
        palette.bgSecondary,
        isInputActive ? palette.primary : palette.borderLight,
      );

      ctx.fillStyle = draftText ? palette.textMain : palette.textMuted;
      ctx.font = '12px sans-serif';
      const previewText = draftText
        ? draftText.slice(0, MAX_DRAFT_LENGTH)
        : '点击这里输入你想说的话';
      ctx.fillText(previewText, inputBox.x + 14, inputBox.y + 26);

      if (isInputActive) {
        const cursorBaseText = draftText ? draftText.slice(0, MAX_DRAFT_LENGTH) : '';
        const cursorX = Math.min(
          inputBox.x + inputBox.width - 30,
          inputBox.x + 16 + ctx.measureText(cursorBaseText).width
        );
        ctx.beginPath();
        ctx.moveTo(cursorX, inputBox.y + 11);
        ctx.lineTo(cursorX, inputBox.y + 33);
        ctx.strokeStyle = palette.primary;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      ctx.fillStyle = palette.textMuted;
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(`${draftText.length}/${MAX_DRAFT_LENGTH}`, inputBox.x + inputBox.width - 10, inputBox.y + 27);
      ctx.textAlign = 'left';

      const sendButton = {
        x: width - 92,
        y: height - 76,
        width: 76,
        height: 44,
        action: 'send',
      };
      buttons.push(sendButton);

      const sendText = app.runStore.sending
        ? '思考中'
        : '发送';
      const sendType = draftText.trim() ? 'primary' : 'ghost';
      drawButton(ctx, sendText, sendButton.x, sendButton.y, sendButton.width, sendButton.height, sendType);
    },

    onTouchStart(point) {
      touchState.startPoint = point;
      touchState.moved = false;
      touchState.startScrollOffset = scrollState.offset;
      touchState.draggingChat = Boolean(
        scrollState.chatRect && isPointInRect(point, scrollState.chatRect)
      );
    },

    onTouchMove(point) {
      if (!touchState.startPoint || !touchState.draggingChat || scrollState.maxOffset <= 0) {
        return;
      }

      const deltaY = point.y - touchState.startPoint.y;
      if (Math.abs(deltaY) > 4) {
        touchState.moved = true;
      }

      scrollState.offset = clamp(
        touchState.startScrollOffset - deltaY,
        0,
        scrollState.maxOffset
      );
    },

    onTouchEnd(point) {
      const moved = touchState.moved;
      touchState.startPoint = null;
      touchState.draggingChat = false;
      touchState.startScrollOffset = scrollState.offset;
      touchState.moved = false;

      if (moved) {
        return;
      }

      const tapped = buttons.find((button) => isPointInRect(point, button));
      if (!tapped) {
        return;
      }

      if (tapped.action === 'back') {
        app.navigate('home');
        return;
      }

      if (app.runStore.sending) {
        return;
      }

      if (tapped.action === 'input') {
        app.openTextComposer();
      } else if (tapped.action === 'send') {
        if (app.runStore.inputDraft.trim()) {
          app.submitDraftMessage();
        } else {
          app.openTextComposer();
        }
      }
    },
  };
}

module.exports = {
  createGameScene,
};

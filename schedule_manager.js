const fs = require('fs');
const path = require('path');

const SCHEDULE_FILE = path.join(__dirname, 'schedule.json');

class ScheduleManager {
  constructor() {
    this.load();
  }

  load() {
    try {
      const data = fs.readFileSync(SCHEDULE_FILE, 'utf8');
      this.data = JSON.parse(data);
    } catch (error) {
      this.data = {
        schedules: [],
        last_updated: new Date().toISOString(),
        auto_reply_enabled: true,
        reply_template: "我是权权老大的虾虾🦞，主人现在{status}，暂时不能及时回复消息。\n\n{schedule_detail}\n\n有什么事情可以先告诉我，等主人忙完会尽快回复你～"
      };
      this.save();
    }
  }

  save() {
    this.data.last_updated = new Date().toISOString();
    fs.writeFileSync(SCHEDULE_FILE, JSON.stringify(this.data, null, 2));
  }

  // 添加日程
  addSchedule(startTime, endTime, activity, location = '') {
    const schedule = {
      id: Date.now().toString(),
      start_time: startTime,
      end_time: endTime,
      activity: activity,
      location: location,
      created_at: new Date().toISOString()
    };
    
    this.data.schedules.push(schedule);
    this.save();
    return schedule;
  }

  // 获取当前活动
  getCurrentActivity() {
    const now = new Date();
    const nowStr = now.toISOString();
    
    for (const schedule of this.data.schedules) {
      if (nowStr >= schedule.start_time && nowStr <= schedule.end_time) {
        return schedule;
      }
    }
    
    return null;
  }

  // 生成回复消息
  generateReply() {
    const current = this.getCurrentActivity();
    
    if (!current) {
      return null; // 没有日程安排，不自动回复
    }

    const status = current.activity;
    let scheduleDetail = '';
    
    if (current.location) {
      scheduleDetail = `📅 日程：${current.activity}\n📍 地点：${current.location}\n⏰ 时间：${this.formatTime(current.start_time)} - ${this.formatTime(current.end_time)}`;
    } else {
      scheduleDetail = `📅 日程：${current.activity}\n⏰ 时间：${this.formatTime(current.start_time)} - ${this.formatTime(current.end_time)}`;
    }

    return this.data.reply_template
      .replace('{status}', status)
      .replace('{schedule_detail}', scheduleDetail);
  }

  // 格式化时间
  formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).replace(/\//g, '-');
  }

  // 清除过期日程
  cleanupExpired() {
    const now = new Date().toISOString();
    this.data.schedules = this.data.schedules.filter(schedule => schedule.end_time > now);
    this.save();
  }

  // 列出所有日程
  listSchedules() {
    this.cleanupExpired();
    return this.data.schedules;
  }

  // 删除日程
  deleteSchedule(id) {
    this.data.schedules = this.data.schedules.filter(schedule => schedule.id !== id);
    this.save();
  }

  // 启用/禁用自动回复
  setAutoReply(enabled) {
    this.data.auto_reply_enabled = enabled;
    this.save();
  }

  // 更新回复模板
  updateTemplate(template) {
    this.data.reply_template = template;
    this.save();
  }
}

// 导出单例
const scheduleManager = new ScheduleManager();
module.exports = scheduleManager;
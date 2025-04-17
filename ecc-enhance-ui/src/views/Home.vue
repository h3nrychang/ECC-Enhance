<template>
    <div class="home">
      <h2>欢迎！ Ciallo～(∠・ω< )⌒★</h2>
      <p>UI Version 0.0.1</p>
      <div class="button-group">
        <a-button
          v-for="item in modules"
          :key="item.path"
          type="primary"
          size="large"
          block
          class="entry-button"
          @click="go(item.path)"
        >
          {{ item.title }} - {{ item.description }}
        </a-button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router'
  
  const router = useRouter()
  const go = (path) => router.push(path)
  
  const modules = [
    { title: '楼园', path: '/park', description: '园区信息管理' },
    { title: '企业', path: '/company', description: '企业信息采集与导入导出' },
    { title: '酒店', path: '/hotel', description: '酒店信息数据处理' },
    { title: '连锁品牌', path: '/chain-band', description: '品牌管理' },
    { title: '连锁门店', path: '/chain-store', description: '门店管理' }
  ]
  </script>
  
  <style scoped>
  .home {
    max-width: 600px;
    margin: 80px auto 0;
    text-align: center;
  }
  .button-group {
    margin-top: 30px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .entry-button {
    font-size: 16px;
    font-weight: 500;
  }
  </style>
  
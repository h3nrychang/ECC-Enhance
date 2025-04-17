import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Park from '@/views/Park.vue'
import Company from '@/views/Company.vue'
import Hotel from '@/views/Hotel.vue'
import ChainBand from '@/views/ChainBand.vue'
import ChainStore from '@/views/ChainStore.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/park', component: Park },
  { path: '/company', component: Company },
  { path: '/hotel', component: Hotel },
  { path: '/chain-band', component: ChainBand },
  { path: '/chain-store', component: ChainStore },
]

export default createRouter({
  history: createWebHistory(),
  routes
})
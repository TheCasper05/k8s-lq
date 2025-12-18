/* This code snippet is setting up a Nuxt plugin that integrates PrimeVue components into a Nuxt.js
application. Here's a breakdown of what each part of the code is doing: */
import PrimeVue from "primevue/config";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Dialog from "primevue/dialog";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Toast from "primevue/toast";
import ToastService from "primevue/toastservice";
import Tooltip from "primevue/tooltip";
import Drawer from "primevue/drawer";
import Avatar from "primevue/avatar";
import Tabs from "primevue/tabs";
import TabList from "primevue/tablist";
import Tab from "primevue/tab";
import TabPanels from "primevue/tabpanels";
import TabPanel from "primevue/tabpanel";
import ProgressBar from "primevue/progressbar";
import Select from "primevue/select";
import Chip from "primevue/chip";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import SelectButton from "primevue/selectbutton";
import Popover from "primevue/popover";
import Menu from "primevue/menu";
import Textarea from "primevue/textarea";
import Message from "primevue/message";
import Stepper from "primevue/stepper";
import StepList from "primevue/steplist";
import Step from "primevue/step";
import StepPanels from "primevue/steppanels";
import StepPanel from "primevue/steppanel";
import InputSwitch from "primevue/inputswitch";
import InputNumber from "primevue/inputnumber";
import Checkbox from "primevue/checkbox";
import RadioButton from "primevue/radiobutton";

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PrimeVue, { ripple: true });
  nuxtApp.vueApp.use(ToastService);

  nuxtApp.vueApp.component("Button", Button);
  nuxtApp.vueApp.component("InputText", InputText);
  nuxtApp.vueApp.component("Dialog", Dialog);
  nuxtApp.vueApp.component("DataTable", DataTable);
  nuxtApp.vueApp.component("Column", Column);
  nuxtApp.vueApp.component("Toast", Toast);
  nuxtApp.vueApp.component("Drawer", Drawer);
  nuxtApp.vueApp.component("Avatar", Avatar);
  nuxtApp.vueApp.component("Tabs", Tabs);
  nuxtApp.vueApp.component("TabList", TabList);
  nuxtApp.vueApp.component("Tab", Tab);
  nuxtApp.vueApp.component("TabPanels", TabPanels);
  nuxtApp.vueApp.component("TabPanel", TabPanel);
  nuxtApp.vueApp.component("ProgressBar", ProgressBar);
  nuxtApp.vueApp.component("Select", Select);
  // Keep Dropdown for backward compatibility during migration
  nuxtApp.vueApp.component("Dropdown", Select);
  nuxtApp.vueApp.component("Chip", Chip);
  nuxtApp.vueApp.component("IconField", IconField);
  nuxtApp.vueApp.component("InputIcon", InputIcon);
  nuxtApp.vueApp.component("SelectButton", SelectButton);
  nuxtApp.vueApp.component("Popover", Popover);
  nuxtApp.vueApp.component("Menu", Menu);
  nuxtApp.vueApp.component("Textarea", Textarea);
  nuxtApp.vueApp.component("Message", Message);
  nuxtApp.vueApp.component("Stepper", Stepper);
  nuxtApp.vueApp.component("StepList", StepList);
  nuxtApp.vueApp.component("Step", Step);
  nuxtApp.vueApp.component("StepPanels", StepPanels);
  nuxtApp.vueApp.component("StepPanel", StepPanel);
  nuxtApp.vueApp.component("InputSwitch", InputSwitch);
  nuxtApp.vueApp.component("InputNumber", InputNumber);
  nuxtApp.vueApp.component("Checkbox", Checkbox);
  nuxtApp.vueApp.component("RadioButton", RadioButton);

  nuxtApp.vueApp.directive("tooltip", Tooltip);
});

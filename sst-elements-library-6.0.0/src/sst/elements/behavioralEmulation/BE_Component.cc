#include "sst_config.h"
#include "BE_Component.h"
#include "Process.h"
#include "Routine.h"
#include "Message.h"
#include "Simulation_Manager.h"
#include "Router.h"
#include <typeinfo>
#include <functional>
#include <ctime>
#include <csignal>
#include "sst/core/event.h"
#include <string>

using namespace SST;
using namespace SST::BEComponent;

beComponent::beComponent(ComponentId_t id, Params& params) :
  Component(id) 
{
  
   
   //printf("Inside the SST component constructor \n");
   bool found;

   //std::cout<<"size of int = "<<sizeof(int)<<"\n";
   self_gid = params.find<int64_t>("Component gid", 0, found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter gid\n");
    }
    
   self_cid = params.find<int64_t>("Component cid", 0, found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter cid\n");
    }

   //if( self_gid == 0) std::cout<<"STARTED LAYOUT BUILD!!!\n";

   //Layout is none as of now
   sys_layout = params.find<std::string>("System Layout", "none", found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter layout\n");
    }

   sys_flags = params.find<std::string>("Flags", "none", found); // -v -i means interpolation sheme -d debug 
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter flags\n");
    }

   self_clock = params.find<int64_t>("Component clock", 0, found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter clock\n");
    } 

   self_kind = params.find<std::string>("Component kind", "none", found); //processor code or link ... config file bgq core- strng
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter kind\n");
    }

   self_ordinal = params.find<int64_t>("Component ordinal", 0, found); //Routing address its like rank 
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter ordinal\n");
    }

   attributes = params.find<std::string>("Attributes", "none", found); //uasge waiting 
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter Attributes\n");
    }

   operations = params.find<std::string>("Operations", "none", found); //
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter operations\n");
    }

   relations = params.find<std::string>("Relations", "none", found); //
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter relations\n");
    }

   properties = params.find<std::string>("Properties", "none", found); //
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter properties\n");
    }

   mailboxes = params.find<std::string>("Mailboxes", "none", found); //
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter mailboxes\n");
    }

   num_links = params.find<int64_t>("num_links", 0, found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter num_links\n");
    }

   topology = params.find<std::string>("Topology", "none", found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter topology\n");
    }

   link_list = params.find<std::string>("Link list", "none", found); //will give the list of gid's which each comp is connected to 
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter link list\n");
    }

   plus_list = params.find<std::string>("Plus links", "none", found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter plus links\n");
    }

   minus_list = params.find<std::string>("Minus links", "none", found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter minus links\n");
    }

    parent = params.find<int64_t>("Parent", 0, found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter parent\n");
    }

    children_s = params.find<std::string>("Children", "none", found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter Children\n");
    }

   containerDimension_list = params.find<std::string>("Container dimensions", "none", found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter container dimensions\n");
    }

   program_file = params.find<std::string>("Software Program", "none", found);
    if (!found) {
        Simulation::getSimulation()->getSimulationOutput().fatal(CALL_INFO, -1,"couldn't find parameter Program\n");
    }

    self_time = 0.0;
    key = 0;
    
    /*std::cout<<"ID="<<id<<std::endl;
    
	  std::cout<<std::endl;
	  std::cout<<std::endl;
	  std::cout<<"id="<<id<<std::endl;
          std::cout<<"self_gid = "<<self_gid<<"\t size is ="<<sizeof(self_gid)<<std::endl;
	  std::cout<<"self_cid = "<<self_cid<<"\t size is ="<<sizeof(self_cid)<<std::endl;	  
	  std::cout<<"sys_layout = "<<sys_layout<<"\t size is ="<<sys_layout.size()<<std::endl;
	  std::cout<<"sys flags = "<<sys_flags<<"\t size is ="<<sys_flags.size()<<std::endl;
	  std::cout<<"self clock = "<<self_clock<<"\t size is ="<<sizeof(self_clock)<<std::endl;
	  std::cout<<"self kind = "<<self_kind<<"\t size is ="<<self_kind.size()<<std::endl;
	  std::cout<<"self ordinal = "<<self_ordinal<<"\t size is ="<<sizeof(self_ordinal)<<std::endl;
	  std::cout<<"Attribute = "<<attributes<<"\t size is ="<<attributes.size()<<std::endl;
	  std::cout<<"Relations = "<<relations<<"\t size is ="<<relations.size()<<std::endl;
	  std::cout<<"Operations = "<<operations<<"\t size is ="<<operations.size()<<std::endl;
	  std::cout<<"Properties = "<<properties<<"\t size is ="<<properties.size()<<std::endl;
	  std::cout<<"mailboxes = "<<mailboxes<<"\t size is ="<<mailboxes.size()<<std::endl;
	  std::cout<<"link_list = "<<link_list<<"\t size is ="<<link_list.size()<<std::endl;
	  std::cout<<"topology = "<<topology<<"\t size is ="<<topology.size()<<std::endl;
	  std::cout<<"num_links = "<<num_links<<"\t size is ="<<sizeof(num_links)<<std::endl;
	  std::cout<<"plus_list = "<<plus_list<<"\t size is ="<<plus_list.size()<<std::endl;
	  std::cout<<"minus_list = "<<minus_list<<"\t size is ="<<minus_list.size()<<std::endl;
	  std::cout<<"parent = "<<parent<<"\t size is ="<<sizeof(parent)<<std::endl;
	  std::cout<<"children_s = "<<children_s<<"\t size is ="<<children_s.size()<<std::endl;
	  std::cout<<"containerDimension_list = "<<containerDimension_list<<"\t size is ="<<containerDimension_list.size()<<std::endl;
	  std::cout<<"program_file = "<<program_file<<"\t size is ="<<program_file.size()<<std::endl;
      
 
    */
   //std::cout<<"Inside C++ program \n";
    componentProcess = std::make_shared<Process>();
    
    
    
    /* Configure the self link for computation events in each Component */
    selfEventLink = configureSelfLink("Selflink", new Event::Handler<beComponent>(this, &beComponent::linkRecvEvent));

    /* register the component clock */
    registerClock(std::to_string(self_clock)+"Hz", new Clock::Handler<beComponent>(this, 
                  &beComponent::clockTic));

    if(self_gid == 0) {
        barrierCount = 0;
        //std::cout<<"LAYOUT BUILD OVER!!!\n";
    }

}


beComponent::~beComponent() 
{

}


beComponent::beComponent() : Component(-1)
{
    // for serialization only
}


void beComponent::setup()
{

  //std::cout<<"Rajashekar";
   //Hello
    /* Python lookup module setup */
    Py_Initialize();
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append(\"/home/raja/SST/sst-elements-library-6.0.0/src/sst/elements/behavioralEmulation/tests\")");
    PyObject* myModuleString = PyString_FromString((char*)"lookup");
    PyObject* myModule = PyImport_Import(myModuleString);
    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"lookupValue");
    
    /* Lookup cache setup */
    std::function<void(std::map<std::tuple<std::string, std::vector<float>>, std::vector<double>>)> updateCache = updateGlobalLookupCache;
    std::function<std::map<std::tuple<std::string, std::vector<float>>, std::vector<double>>()> getCache = getGlobalLookupCache;

    /* Build the simulation handler for the component */
    //if(self_gid > 0) std::cout<<"\n"<<self_gid<<"- Simulation handler build started!\n";
    simulation_handler = std::make_shared<simManager>(self_gid, self_cid, self_ordinal, parent, operations, relations, properties, 
                                                      mailboxes, topology, containerDimension_list, plus_list, minus_list, 
                                                      children_s, sys_flags, myFunction, updateCache, getCache);

   //Raja - why this ?
    if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Simulation handler build successful!\n";

    /* configure out links */
    std::vector<std::string> link_gids;
    int l_gid;
    link_gids = decode(link_list.substr(1, link_list.size()-2), ", ");

    for(int i = 0; i < num_links; i++){
        l_gid = stoi(link_gids[i]);
        C_Link[l_gid] = configureLink("Link "+link_gids[i], new Event::Handler<beComponent>(this, &beComponent::linkRecvEvent));
	  assert(C_Link[l_gid]);
    }

    /* Set up executor process if there is an application program to be run */
    if(program_file != "none")
    {
      // tell the simulator not to end without us if component has an executor process
      primaryComponentDoNotEndSim();

      std::shared_ptr<Executor> executor = std::make_shared<Executor>(self_gid, simulation_handler->giveExecutorId(), program_file, simulation_handler, simulation_handler->hardware_state);
  
      if (self_gid == 9)
	std::cout<<"Debug value is :"<<simulation_handler->sim_flags->debug<<"\n";
      if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Simulation handler build successful!\n";

      componentProcess->append(executor);

    }

    else
    {
      componentProcess->type = "Master Wait Process";
    }

    /* Run the simulation */
    run(componentProcess);    

}


std::vector<std::string> beComponent::decode(std::string operand, std::string delimiter)
{	

    size_t pos = 0;
    std::vector<std::string> operandList;

    while((pos = operand.find(delimiter)) != std::string::npos){           
        operandList.push_back(operand.substr(0, pos));
        operand.erase(0, pos + delimiter.length());
    }
    operandList.push_back(operand);

    return operandList;
            
}


/*void beComponent::generateTrace(std::shared_ptr<simEvent> event, std::shared_ptr<Process> process, bool endOfEvent, bool messagePathTrace, std::tuple<int, int, int, std::vector<int>> messageParams)
{

    if(endOfEvent)
    {
	
	if(messagePathTrace)	//Check for non blocking communication
        {
	    double endtime = getCurrentSimTimeNano()/1000000000.0;
            std::shared_ptr<Routine> routine = std::dynamic_pointer_cast<Routine>(process);

	    for(int i = comm_records.size()-1; i >= 0; i--) 
            {
		if( (std::get<2>(std::get<2>(comm_records[i])) == routine->eventId) && (std::get<1>(std::get<2>(comm_records[i])) == routine->gid) ) {
                    std::get<1>(std::get<1>((std::get<4>(comm_records[i]))[0])) = endtime; //comm_records[i][-1][-1][1][-1] = endtime
                    break;
                }
            }

        }

        else
        {
	    double endtime = getCurrentSimTimeNano()/1000000000.0;
            std::shared_ptr<Routine> routine = std::dynamic_pointer_cast<Routine>(process);
            
            for(int i = call_records.size()-1; i >= 0; i--) 
            {
		if((std::get<2>(call_records[i]))[1] == routine->eventId) {
                    (std::get<4>(call_records[i])).back() = endtime; //call_records[i][4][-1] = endtime
                    break;
                }
            }

        }

    }

    else
    {
	
	if(messagePathTrace)
        {
            std::vector< std::tuple<int, std::tuple<double, double>, std::string, std::vector<int>, std::vector<int>> > message_path;

            if(event == NULL)
            {
                double starttime = getCurrentSimTimeNano()/1000000000.0;

                std::tuple<double, double> time_pair = std::make_tuple(starttime, starttime);
                std::string lookup_file = "None";
                std::vector<int> parameters;
                std::vector<int> locations = std::get<3>(messageParams);

                std::tuple<int, int, int> sid_pair = std::make_tuple(std::get<0>(messageParams), locations[0], std::get<2>(messageParams));
                std::tuple<int, int> rid_pair = std::make_tuple(std::get<1>(messageParams), 0); 

		message_path.push_back(make_tuple(self_gid, time_pair, lookup_file, parameters, locations));

                comm_records.push_back(make_tuple(locations[0], "comm", sid_pair, rid_pair, message_path));

            }

            else
            {
                std::shared_ptr<subprocessEvent> ev = std::dynamic_pointer_cast<subprocessEvent>(event);
                std::shared_ptr<Routine> routine = std::dynamic_pointer_cast<Routine>((ev->processes).front());     // will we ever have more than one routine in interconnect component

                std::vector<int> parameters = std::get<0>(routine->getRoutineParams());
                parameters.push_back(std::get<2>(messageParams));

                std::string lookup_file = std::get<0>(simulation_handler->operations[std::get<0>(simulation_handler->mailboxes)]);
           
                double starttime = getCurrentSimTimeNano()/1000000000.0;

                std::tuple<double, double> time_pair = std::make_tuple(starttime, 0.0);
                std::tuple<int, int, int> sid_pair = std::make_tuple(std::get<0>(messageParams), routine->gid, routine->eventId);
                std::tuple<int, int> rid_pair = std::make_tuple(std::get<1>(messageParams), 0); 
                std::vector<int> locations = std::get<3>(messageParams);

                message_path.push_back(make_tuple(self_gid, time_pair, lookup_file, parameters, locations));

                comm_records.push_back(make_tuple(routine->gid, "comm", sid_pair, rid_pair, message_path));
            }

        }

        else
        {
            std::shared_ptr<Executor> executor = std::dynamic_pointer_cast<Executor>(process);
	    std::vector<Instruction>::iterator instruction = executor->getCurrentInstruction();
            std::map<std::string, int> registers = executor->getRegisterSet();
            double starttime;

            if(instruction->kind == "call")
            {
		std::string event_type = (instruction->operands)[1];
                std::vector<int> parameters;
                std::shared_ptr<subprocessEvent> ev = std::dynamic_pointer_cast<subprocessEvent>(event);
                std::shared_ptr<Routine> routine = std::dynamic_pointer_cast<Routine>((ev->processes).front());

                for(int i = 2; i < (instruction->operands).size(); i++) {
                    if(((instruction->operands)[i])[0] == 'r') parameters.push_back(registers[(instruction->operands)[i]]);
                    else parameters.push_back(stoi((instruction->operands)[i]));
                }

                int event_id = routine->eventId;
                int thread_id = self_cid;
                starttime = getCurrentSimTimeNano()/1000000000.0;
                std::string lookup_file = std::get<0>(simulation_handler->operations[event_type]);

                std::vector<int> id_pair;
                std::vector<double> time_pair;
                id_pair.push_back(thread_id);
                id_pair.push_back(event_id);
                time_pair.push_back(starttime);
                time_pair.push_back(0.0);

                call_records.push_back(make_tuple(self_gid, instruction->kind, id_pair, event_type, time_pair, lookup_file, parameters));
            }

            else if(instruction->kind == "comm")
            {
                std::shared_ptr<subprocessEvent> ev = std::dynamic_pointer_cast<subprocessEvent>(event);
                std::shared_ptr<Message> message = std::dynamic_pointer_cast<Message>((ev->processes).front());
                int sthread_id = self_cid;
                int sevent_id = message->eventId;
                int rthread_id;
                starttime = getCurrentSimTimeNano()/1000000000.0;

                if(((instruction->operands)[2])[0] == 'r') rthread_id = registers[(instruction->operands)[2]];
                else rthread_id = stoi((instruction->operands)[2]);

                std::vector< std::tuple<int, std::tuple<double, double>, std::string, std::vector<int>, std::vector<int>> > message_path;
                std::vector<int> parameters;

                std::tuple<double, double> time_pair = std::make_tuple(starttime, starttime);
                std::tuple<int, int, int> sid_pair = std::make_tuple(sthread_id, self_gid, sevent_id);
                std::tuple<int, int> rid_pair = std::make_tuple(rthread_id, 0);
                std::vector<int> locations;

                message_path.push_back(make_tuple(self_gid, time_pair, "None", parameters, locations));

                comm_records.push_back(make_tuple(self_gid, instruction->kind, sid_pair, rid_pair, message_path));
            }          

        }

    }
    
} */


beCommEvent* beComponent::buildLinkEvent(std::string type, int so, int tar, std::vector<int> tlist, std::vector<int> list, int coid, std::string opp, std::string opid, std::string st)
{
    beCommEvent* bev = new beCommEvent();

    //std::cout<<"buildLinkEvent -> tarlist \n";
 /*   for(std::vector<int>::iterator i = tlist.begin(); i != tlist.end(); i++)
    {
      int start_value = 2+simulation_handler->containerDimensions[0]+simulation_handler->containerDimensions[1]+simulation_handler->containerDimensions[2];
      int cfl = (*i-1)%(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]);
      int br = floor((*i-1)/(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
      int bds = floor((*i-1)/(simulation_handler->containerDimensions[1]*simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
      int new_target = start_value + cfl + (br*((simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3])+simulation_handler->containerDimensions[2]))+(bds*simulation_handler->containerDimensions[1]);
      std::cout<<"Old target is ="<<*i<<"\t New target is ="<<new_target<<"\n";    
    //  *i = new_target;
    }*/
     
    bev->type 		= type;
    bev->source 	= so;
    bev->target 	= tar;
    bev->tarlist	= tlist;
    bev->list 		= list;
    bev->comp_id 	= coid;
    bev->op_param 	= opp;
    bev->op_id 		= opid;
    bev->sub_type 	= st;
    
    return bev;
}


void beComponent::step(std::shared_ptr<Process> process)
{
    if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Stepping through " << process->type << std::endl; 
    
    std::shared_ptr<simEvent> event = process->run();

    if (event != nullptr)
    {
        if(process->type == "Executor")
        {
            std::vector<int> empty;
            //generateTrace(event, process, false, false, std::make_tuple(0, 0, 0, empty)); //generate event trace for compute events and communicate events at the source
        }

        std::string event_type = event->type;
	double delay;

        if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- " << event_type << " event returned" << std::endl;
	
	if (event_type == "timeout")
        {
	  
            auto ev = std::dynamic_pointer_cast<timeoutEvent>(event);	
            //delay = ev->value*self_clock;
            delay = ev->value;
	}

	else
            delay = 0;
	
	  
	double eventTime = self_time + delay;		
	
	
	
	if (event_type == "condition")
        {
	    auto ev = std::dynamic_pointer_cast<conditionEvent>(event);
            double value = simulation_handler->hardware_state[ev->attribute];//ev->state[ev->attribute];

            if (ev->conditionFunction(value, ev->value))
            {
                if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Condition satisfied" << std::endl;
                tick(eventTime, ev, process);
            }
            else
            {
                if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Condition not satisfied---notifying the necessary components" << std::endl;
	        watchList[key] = make_tuple(ev, process);//do we need unique id for object?
                key++;
            }

        }

        else if (event_type == "wait")
        {
            auto ev = std::dynamic_pointer_cast<waitEvent>(event);
            waitQ.push(std::make_tuple(ev, process));//?????waiting[eventTime]
        }

        else if (event_type == "barrier")
        {         
            std::vector<int> empty;
            auto barrier_ev = std::dynamic_pointer_cast<barrierEvent>(event);

            beCommEvent *bev;
            bev = buildLinkEvent("barrier", barrier_ev->source, barrier_ev->commgroup, empty, empty, -1, "", "", "");

            barrierQ.push(std::make_tuple(barrier_ev, process));

            if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- waiting on barrier primitive"<<"\n";

            C_Link[0]->send(bev);
        }

        else if (event_type == "receiveWait")
        {
            auto ev = std::dynamic_pointer_cast<recvWaitEvent>(event);
            bool present = false;
            std::shared_ptr<Routine> routine = std::dynamic_pointer_cast<Routine>(process);

            int msg_source = std::get<0>(routine->getRoutineParams())[1];

            for(auto itr = messageTable.begin(); itr != messageTable.end(); itr++) {

                if (msg_source == itr->first && !((itr->second).empty())) {
                    std::shared_ptr<Process> mprocess;
                    std::shared_ptr<simEvent> mevent;
                    std::tie(mevent, mprocess) = (itr->second).front();
                    (itr->second).pop();
                    tick(self_time, mevent, mprocess);
                    tick(self_time, ev, process);
                    present = true;
                }

            }

            if(!present) (recvTable[msg_source]).push(std::tie(ev, process));
             
        }

        else if (event_type == "receive")
        {
            auto ev = std::dynamic_pointer_cast<recvEvent>(event);
            bool present = false;
            std::shared_ptr<Routine> routine = std::dynamic_pointer_cast<Routine>(process);

            if((std::get<0>(routine->getRoutineParams())).empty()) 
                throw std::runtime_error("Receive/unwait expecting the message source as input!! (Add source to the lambda function of unwait operation)");

            int msg_source = std::get<0>(routine->getRoutineParams())[0];

            for(auto itr = recvTable.begin(); itr != recvTable.end(); itr++) {

                if (msg_source == itr->first && !((itr->second).empty())) {
                    std::shared_ptr<Process> rprocess;
                    std::shared_ptr<simEvent> revent;
                    std::tie(revent, rprocess) = (itr->second).front();
                    (itr->second).pop();
                    tick(self_time, revent, rprocess);
                    tick(self_time, ev, process);
                    present = true;
                }

            }

            if(!present) (messageTable[msg_source]).push(std::tie(ev, process));
             
        }			

	else if (event_type != "timeout")
        {		
            tick(eventTime, event, process);
	}
/*
	else
        {
            auto ev = std::dynamic_pointer_cast<timeoutEvent>(event);

            computeQ.push(std::make_tuple(eventTime, ev, process));

            std::vector<int> empty;
            beCommEvent *bev;
            bev = buildLinkEvent(ev->type, -1, -1, empty, empty, -1, "", "", "");
            selfEventLink->send(ev->value*self_clock, bev);
	}
*/
	else
        {
//	  std::cout<<"else\n";
            auto ev = std::dynamic_pointer_cast<timeoutEvent>(event);
            std::vector<int> empty;           

            if(simulation_handler->hardware_state["usage"] == 0.0)
            {
	      //std::cout<<"Inside if Line604\n";
                computeQ.push(std::make_tuple(eventTime, ev, process));
                simulation_handler->hardware_state["usage"] = 1.0;

                beCommEvent *bev;
                bev = buildLinkEvent(ev->type, -1, -1, empty, empty, -1, "", "", "");
		//if(self_gid==1)
		//std::cout<<"Before linkRecvEvnet \n";
                selfEventLink->send(ev->value*self_clock, bev);
		//if(self_gid==1)
		//std::cout<<"After linkRecvEvnet \n";
            }

            else
	    {
	      //std::cout<<"Inside else Line 616\n";
	      computeWaitQ.push(std::make_tuple(ev, process));
	    }

	}

    }

    else
    {
        if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Event in this process is now null \n";

        if(process->type == "Routine") 
        {
            std::shared_ptr<Routine> routine = std::dynamic_pointer_cast<Routine>(process);
            std::vector<int> empty;

            //if(process->parent->type == "Executor") generateTrace(NULL, process, true, false, std::make_tuple(0, 0, 0, empty));
            //else if(routine->creator == "comm") generateTrace(NULL, process, true, true, std::make_tuple(0, 0, 0, empty));
        }

        process->selfDelete();
  
	if (process->parent->children.empty())
	    step(process->parent);
	
	process->parent = nullptr;
    }

}


void beComponent::tick(double eventTime, std::shared_ptr<simEvent> event, std::shared_ptr<Process> eventProcess)
{
    //std::cout<<"Inside Tick \n";

    if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Inside tick for the event " << event->type << std::endl;

    eventProcess->state = simulation_handler->hardware_state;

    handleEvents(event, eventProcess); 
	
    if (eventProcess->children.empty() && eventProcess->parent != NULL)
    {
	step(eventProcess);
    }

}


void beComponent::run(std::shared_ptr<Process> process)
{ 
    std::stack<std::shared_ptr<Process>> children_q = process->children; 

    if (!children_q.empty())
    {
        while(!children_q.empty())
        {
	    run(children_q.top());
            children_q.pop();
	}
    }

    else
	step(process);

}


int beComponent::getCurrentTime()
{ 
    return 0;//(int) getCurrentSimTimeNano(); 
}


/* Does nothing during a clock tick as it is discrete event simulation */
bool beComponent::clockTic( Cycle_t )
{
    return false;                              
}


// incoming messages are scanned and deleted
void beComponent::linkRecvEvent(Event *ev) 
{
//    if(self_gid==1)
  //  std::cout<<"Inside linkRecvEvnet \n";
    //std::cout<<"Every time ? \n";
    beCommEvent *link_event = dynamic_cast<beCommEvent*>(ev);
    

    if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Event received here for "<<self_kind<<". It is "<<link_event->type<<"\n";

    if (link_event)
    {     
	//std::cout<<"If link_event \n";
/*
        if(link_event->type == "timeout")
        {
            std::tuple<double, std::shared_ptr<timeoutEvent>, std::shared_ptr<Process>> entry = computeQ.front(); 

            //double eventTime = std::get<0>(entry);

	    std::shared_ptr<simEvent> event = std::get<1>(entry);
	    std::shared_ptr<Process> eventProcess = std::get<2>(entry);

            computeQ.pop();

            tick(self_time, event, eventProcess);

            delete link_event;

        }
*/
        if(link_event->type == "timeout")
        {
	  	//std::cout<<"If link_event type is timeout\n";
            std::tuple<double, std::shared_ptr<timeoutEvent>, std::shared_ptr<Process>> entry = computeQ.front(); 

	    std::shared_ptr<simEvent> event = std::get<1>(entry);
	    std::shared_ptr<Process> eventProcess = std::get<2>(entry);

            computeQ.pop();

            delete link_event;

            simulation_handler->hardware_state["usage"] = 0.0;

            if(!computeWaitQ.empty())
            {
		std::tuple<std::shared_ptr<timeoutEvent>, std::shared_ptr<Process>> pentry = computeWaitQ.front();
                computeWaitQ.pop();
            
                std::shared_ptr<timeoutEvent> pev = std::get<0>(pentry);
	        std::shared_ptr<Process> pevProcess = std::get<1>(pentry);
                std::vector<int> empty;

                computeQ.push(std::make_tuple(self_time, pev, pevProcess));

                simulation_handler->hardware_state["usage"] = 1.0;

                beCommEvent *bev;
                bev = buildLinkEvent(pev->type, -1, -1, empty, empty, -1, "", "", "");

                selfEventLink->send(pev->value*self_clock, bev);
            }
            tick(self_time, event, eventProcess);

        }

        else if(link_event->type == "communicate")
        {
            
	  //	std::cout<<"If link_event type is communicate\t";
            std::queue<std::shared_ptr<Process>> routines;
	   // if(link_event->target == 6)
	     // std::cout<<"Self ordinal is ="<<self_ordinal<<"\t Target ="<<link_event->target<<"\n";

	    int start_value = 2+simulation_handler->containerDimensions[0]+simulation_handler->containerDimensions[1]+simulation_handler->containerDimensions[2];
	    int cfl = (self_ordinal-1)%(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]);
	    int br = floor((self_ordinal-1)/(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
	    int bds = floor((self_ordinal-1)/(simulation_handler->containerDimensions[1]*simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
	    int new_target = 1+start_value + cfl + (br*((simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3])+simulation_handler->containerDimensions[2]))+(bds*simulation_handler->containerDimensions[1]);
 	    if(link_event->target == 30)
	      std::cout<<"Local ID ="<<self_ordinal<<"\t New Target ="<<new_target<<"\t Actual target ="<<link_event->target<<"\n";
	   
 	    bool isDestination = (new_target == link_event->target);
	   
            	    
	    if(link_event->target == 30)
	      std::cout<<"destination is ="<<isDestination<<"\n";

//	    bool isDestination = (self_ordinal == link_event->target);	    
	    //std::cout<<"LINK EVENT -> Target"<<link_event->type<<link_event->source<<link_event->target<<link_event->tarlist<<link_event->list<<link_event->comp_id<<link_event->op_param<<link_event->op_id<<link_event->sub_type<<"\n";
// 	    if(link_event->target == 50)
// 	    {
// 	      std::cout<<"Link event list \n";
// 	      for(std::vector<int>::iterator i = link_event->list.begin(); i != link_event->list.end(); i++)
// 		std::cout<<*i<<"\t";
// 	      std::cout<<"\n";
// 	    }

            (link_event->list).push_back(self_gid);

            if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Event revd from "<<(link_event->list)[0]<<" (GID)"<<"\n";

            routines = simulation_handler->dynamic_mailbox_routines(link_event->list, link_event->tarlist, link_event->comp_id, link_event->source, link_event->target, stoi(link_event->op_param), stoi(link_event->op_id), link_event->sub_type, isDestination);

            if (!routines.empty())
            {
	      if(link_event->target == 30)
		std::cout<<"Routine not empty"<<"\n";

	      
//	        if(link_event->target == 6)
//	      	    if(link_event->target == 50)
//		  std::cout<<"Routine not empty \n";
                std::shared_ptr<simEvent> routine_event = std::make_shared<subprocessEvent>(routines);
               // std::cout<<"Inside routine check before tick \n";
		tick(link_event->eventTime, routine_event, componentProcess);
		//std::cout<<"Inside routine check after Tick \n";
		if (isDestination)
                {
		  int next_hop = -1;
		    if(link_event->target == 30)
		      std::cout<<"I have reached\n";
                    if(link_event->sub_type == "blocking") {
                        next_hop = link_event->list[(link_event->list).size() - 2];  // last element is the destination. So, send event to the one before that

                        beCommEvent *bev;
                        bev = buildLinkEvent("acknowledge", -1, -1, link_event->tarlist, link_event->list, 
                                             link_event->comp_id, "", "", "");

                        if(next_hop == self_gid) selfEventLink->send(bev);  
                        else if(next_hop >= 0) C_Link[next_hop]->send(bev);
                    }

                }

            }

            else
            {
	        std::cout<<"Inside communication"<<"\n";
                int next_hop = -1;
                int hier_target = (link_event->tarlist).back();
		//std::cout<<"Tarlist \n";
		//for(int i=0;i<link_event->tarlist.size();i++)
		//{
		  //std::cout<<link_event->tarlist[i]<<"\t";
		//}
                int targetOneLevelDown = -1;

                if((link_event->tarlist).size() > 1) targetOneLevelDown = (link_event->tarlist).end()[-2];
		std::cout<<"isDestination before ->"<<isDestination<<"\n";
                /* If it is destination core - destination component creating acknowledge event if it is a blocking communication */
                if (isDestination)
                {
		    if(link_event->target == 30)
		      std::cout<<"I have reached\n";
                    if(link_event->sub_type == "blocking") {
                        next_hop = link_event->list[(link_event->list).size() - 2];  // last element is the destination. So, send event to the one before that

                        beCommEvent *bev;
                        bev = buildLinkEvent("acknowledge", -1, -1, link_event->tarlist, link_event->list, 
                                             link_event->comp_id, "", "", "");

                        if(next_hop == self_gid) selfEventLink->send(bev);  
                        else if(next_hop >= 0) C_Link[next_hop]->send(bev);
                    }

                }

                else if(self_ordinal == -1) //not an unique classifier for links - change by passing kind of the BEO as a parameter to simulation!!
                {
                    int other_end = link_event->list[(link_event->list).size() - 2];
                 
                    for(auto itr = C_Link.begin(); itr != C_Link.end(); itr++) {
                        if(itr->first == other_end) continue;
                        else next_hop = itr->first;
                    }

                    beCommEvent *bev;
                    bev = buildLinkEvent(link_event->type, link_event->source, link_event->target, link_event->tarlist, link_event->list, 
                                         link_event->comp_id, link_event->op_param, link_event->op_id, link_event->sub_type);

                    if(next_hop >= 0) C_Link[next_hop]->send(bev);
                }
                
                /* If it is intermediate core or a container object*/
                else
                {
		    int local_target=0;
		    //std::cout<<"\n \n I am here for nexthop\n";
		    //std::cout<<"1-> "<<hier_target<<"--2-->  "<<targetOneLevelDown<<"\n";
		    /*std::cout<<"Target ="<<hier_target<<"\n";
		    int start_value = 2+simulation_handler->containerDimensions[0]+simulation_handler->containerDimensions[1]+simulation_handler->containerDimensions[2];
		    int cfl = (hier_target-1)%(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]);
		    int br = floor((hier_target-1)/(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
		    int bds = floor((hier_target-1)/(simulation_handler->containerDimensions[1]*simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
		    int new_target = start_value + cfl + (br*((simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3])+simulation_handler->containerDimensions[2]))+(bds*simulation_handler->containerDimensions[1]);
		    std::cout<<"Old target is ="<<hier_target<<"\t New target is ="<<new_target<<"\n";    
		      //  *i = new_target;*/
		    int total_size = (simulation_handler->containerDimensions[0]*simulation_handler->containerDimensions[1]*simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]); 
		    start_value = 2+simulation_handler->containerDimensions[0]+simulation_handler->containerDimensions[1]+simulation_handler->containerDimensions[2];
		    local_target;
		   for(int i=0;i<total_size;i++)
		    {
		        int t = i+1;
			int cfl = (t-1)%(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]);
			int br = floor((t-1)/(simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
			int bds = floor((t-1)/(simulation_handler->containerDimensions[1]*simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3]));
			int new_target = start_value + cfl + (br*((simulation_handler->containerDimensions[2]*simulation_handler->containerDimensions[3])+simulation_handler->containerDimensions[2]))+(bds*simulation_handler->containerDimensions[1]);
			if(new_target == hier_target)
			{
			  local_target = i;
			  break;
			}
		    }
//		    	    if(link_event->target == 50){
//		    std::cout<<"Target ="<<hier_target<<"\t";
//		    std::cout<<"BE Component.cc -> local target ="<<local_target<<"\n\n";
//			    }
		    std::tuple<bool, int, int> route_set = (simulation_handler->dynamicRouter)->findNextHop(hier_target, targetOneLevelDown,local_target);
  //                  if(link_event->target == 50)
//		    std::cout<<"next hop details= 1-> "<<std::get<0>(route_set)<<"  Link ="<<std::get<1>(route_set)<<"  Target ="<<std::get<2>(route_set)<<"\n";
		    next_hop = std::get<1>(route_set);

                    if(std::get<0>(route_set) == 1) (link_event->tarlist).push_back(std::get<2>(route_set));

                    else if(std::get<0>(route_set) == -1) (link_event->tarlist).pop_back();

                    beCommEvent *bev;
                    bev = buildLinkEvent(link_event->type, link_event->source, link_event->target, link_event->tarlist, link_event->list, 
                                            link_event->comp_id, link_event->op_param, link_event->op_id, link_event->sub_type);

                    if(next_hop >= 0) C_Link[next_hop]->send(bev);
                }
            }   

            delete link_event;                   
          
        }

        else if(link_event->type == "acknowledge")  // acknowledge after the destination completes its routine?
        {
            //auto ack_ev = std::dynamic_pointer_cast<ackEvent>(link_event->event);
            std::vector<int> locations = link_event->list;
            std::queue<std::shared_ptr<Process>> routines;

            for(int j = 0; j < locations.size()-1; j++)
            {
                if( self_gid == locations[j])
                {
                    //routines = simulation_handler->ack_routines(locations, link_event->comp_id, link_event->source, link_event->target, 1, -1, link_event->sub_type);

		    if (!routines.empty())
                    {
                        std::shared_ptr<simEvent> routine_event = std::make_shared<subprocessEvent>(routines);

                        tick(link_event->eventTime, routine_event, componentProcess);
                    }

                    else
                    {
                        int next_hop = locations[j+1];

                        beCommEvent *bev;

                        bev = buildLinkEvent(link_event->type, -1, -1, link_event->tarlist, link_event->list, 
                                             link_event->comp_id, "", "", "");

                        //bev->event = ack_ev;
                        //bev->eventTime = self_time;

                        if(next_hop >= 0) C_Link[next_hop]->send(bev);
                    }

                    break;
                }
            }

            if (self_gid == locations.back() && !waitQ.empty())
            {
                //printf("Blocking Completion initiated by %d is complete\n", self_gid);
	        std::tuple<std::shared_ptr<simEvent>, std::shared_ptr<Process>> entry = waitQ.front();      //Change waitQ and acknowledge event to support process id
	        std::shared_ptr<simEvent> event;
	        std::shared_ptr<Process> eventProcess;

	        event = std::get<0>(entry);
	        eventProcess = std::get<1>(entry);

                waitQ.pop();
                if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- received ack from "<<locations.back()<<" for "<<eventProcess->type<<"\n";

                tick(self_time, event, eventProcess); 
            }

            delete link_event;                

        }   

        else if(link_event->type == "barrier")
        {

            if( self_gid == 0)
            {
                int source = link_event->source;
                int group_count = link_event->target;

                barrierCount++;

                if(barrierCount < group_count)
                {
                    barrierList.push(source);
                }

                else 
                {
                    barrierList.push(source);
                    barrierCount = 0;
                    while(!barrierList.empty()) { 
                        beCommEvent *bev;
                        bev = buildLinkEvent(link_event->type, link_event->source, link_event->target, link_event->tarlist, link_event->list, 
                                             link_event->comp_id, link_event->op_param, link_event->op_id, link_event->sub_type);

                        C_Link[barrierList.front()]->send(bev);
                        barrierList.pop();
                    }        
                }
                
            }

            else
            {
                std::shared_ptr<Process> process; 
                std::tuple<std::shared_ptr<simEvent>, std::shared_ptr<Process>> entry = barrierQ.front();
	        std::shared_ptr<simEvent> event;

	        event = std::get<0>(entry);
	        process = std::get<1>(entry);

                barrierQ.pop(); 

                tick(self_time, event, process);
            }
                              
            delete link_event;

        } 

        else if(link_event->type == "call")
        {
            if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Call Event received here for "<<self_kind<<". Called by "<<link_event->source<<" for "<<link_event->op_id<<"\n";
 
            std::vector<int> integerInputs = link_event->list;
            std::vector<float> floatInputs(integerInputs.begin(), integerInputs.end());

            std::queue<std::shared_ptr<Process>> routine_queue;
            auto routine = simulation_handler->call(0, link_event->source, link_event->comp_id, link_event->target, link_event->op_param, link_event->op_id, floatInputs, link_event->sub_type);
    	    routine_queue.push(routine);

    	    std::shared_ptr<simEvent> routine_event = std::make_shared<subprocessEvent>(routine_queue);
            tick(self_time, routine_event, componentProcess);
                              
            delete link_event;

        }      

    }   

    else 
    {
        throw std::runtime_error("Error! Bad Event Type!\n");//printf("Error! Bad Event Type!\n");
    }

}


void beComponent::handleEvents(std::shared_ptr<simEvent> event, std::shared_ptr<Process> eventProcess)
{
    std::string event_type = event->type;

    if (event_type == "change")
    {
        auto ev = std::dynamic_pointer_cast<changeEvent>(event);        
        ev->state[ev->attribute] = ev->value;

        simulation_handler->hardware_state[ev->attribute] = ev->value;

        if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling change event\n", self_gid);
        //if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"Watchlist length is "<<watchList.size()<<"\n";
        
        bool process_ready = false;     
        std::shared_ptr<conditionEvent> cond_event;
        std::shared_ptr<Process> cond_process;

        for (auto itr = watchList.begin(); itr != watchList.end(); itr++)         //Might have bugs...check!!!
        {         
            cond_event = std::get<0>(itr->second);
            cond_process = std::get<1>(itr->second);

            if(cond_event->conditionFunction(simulation_handler->hardware_state[cond_event->attribute], cond_event->value))
            {
                watchList.erase(itr);
                process_ready = true;
                //if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"Executing one waiting routine process from the watchList\n";
                break;
            }
        }
             
        if(process_ready == true) tick(self_time, cond_event, cond_process);
          
    }

    else if (event_type == "timeout")
    {
	if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling timeout event\n", self_gid);
    }

    else if (event_type == "condition")
    {
	if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling condition event\n", self_gid); 
    }

    else if (event_type == "communicate")
    {
        auto comm_event = std::dynamic_pointer_cast<commEvent>(event);
        int next_hop = -1;

        if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Forwarding the message to the next component %d\n", self_gid, next_hop);

        /* calculate next hop */ 
        if(self_ordinal != -1)
        {
            int hier_target = (comm_event->tarlist).back();
            int targetOneLevelDown = -1;

            if((comm_event->tarlist).size() > 1) targetOneLevelDown = (comm_event->tarlist).end()[-2];
	    
	    std::cout<<"Before calling findNextHop \n";

            std::tuple<bool, int, int> route_set = (simulation_handler->dynamicRouter)->findNextHop(hier_target, targetOneLevelDown, hier_target);

            next_hop = std::get<1>(route_set);

            if(std::get<0>(route_set) == 1) (comm_event->tarlist).push_back(std::get<2>(route_set));

            else if(std::get<0>(route_set) == 1) (comm_event->tarlist).pop_back();
        }

        else
        {
            int other_end = comm_event->locations[(comm_event->locations).size() - 2];
                 
            for(auto itr = C_Link.begin(); itr != C_Link.end(); itr++) 
            {
                if(itr->first == other_end) continue;
                else next_hop = itr->first;
            }
        }

        beCommEvent *bev;
        bev = buildLinkEvent(comm_event->type, comm_event->source, comm_event->target, comm_event->tarlist, comm_event->locations, comm_event->pid, 
                             std::to_string(comm_event->size), std::to_string(comm_event->tag), comm_event->comm_type);

        if(next_hop >= 0) C_Link[next_hop]->send(bev);
                
    }

    else if (event_type == "initiate communication")
    {
	if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling communication initiation\n", self_gid);

        auto messageProcess = std::dynamic_pointer_cast<Message>(eventProcess);
        auto comm_event = std::dynamic_pointer_cast<commEvent>(event);

        (comm_event->tarlist).push_back(comm_event->target);

        beCommEvent *bev;
        bev = buildLinkEvent("communicate", comm_event->source, comm_event->target, comm_event->tarlist, comm_event->locations, comm_event->pid, 
                             std::to_string(comm_event->size), std::to_string(comm_event->tag), comm_event->comm_type);

        selfEventLink->send(bev);
                
    }

    else if (event_type == "call")
    {
        auto call_event = std::dynamic_pointer_cast<callEvent>(event);

        std::vector<float> floatInputs = call_event->inputs;
        std::vector<int> integerInputs(floatInputs.begin(), floatInputs.end());
        std::vector<int> empty;

        beCommEvent *bev;
        bev = buildLinkEvent(call_event->type, call_event->source_gid, call_event->target_gid, empty, integerInputs,  
                             call_event->source_pid, call_event->target_family, call_event->operation, call_event->call_type);

        int target = call_event->target_gid;

        if(target >= 0) C_Link[target]->send(bev);
        if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Calling the component "<<target<<"\n";
                
    }

    else if (event_type == "acknowledge")
    {
        auto ack_ev = std::dynamic_pointer_cast<ackEvent>(event);

        std::vector<int> locations = ack_ev->locations;
        std::vector<int> empty;
        int pid = ack_ev->pid;
        int nxt_hop = ack_ev->next_hop;

        beCommEvent *bev;
        bev = buildLinkEvent("acknowledge", -1, -1, empty, locations, pid, "1", "", "");

        if((simulation_handler->sim_flags)->debug == self_gid) std::cout<<"GID: "<<self_gid<<" -- Sending ack to "<<nxt_hop<<" from "<<self_gid<<"\n";
        
        if(nxt_hop == self_gid) selfEventLink->send(bev);
        else if(nxt_hop >= 0) C_Link[nxt_hop]->send(bev);        
    }

    else if (event_type == "subprocess")
    {
        auto ev = std::dynamic_pointer_cast<subprocessEvent>(event);
                
        if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling subprocess event\n", self_gid);
		
        while (!ev->processes.empty())
        {                      
	    eventProcess->append(ev->processes.front()); //what if there are more than one routines in the sub process event 		
	    step(ev->processes.front());
	    ev->processes.pop(); 
	}

    }

    else if (event_type == "autoprocess")
    {
	auto ev = std::dynamic_pointer_cast<autoprocessEvent>(event);

        if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling autoprocess event\n", self_gid);
	
	while (!ev->processes.empty())
        {
	    componentProcess->append(ev->processes.front());
	    step(ev->processes.front());
	    ev->processes.pop();
	}

    }

    else if (event_type == "barrier")
    {
        if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling barrier event\n", self_gid);
    }

    else if (event_type == "wait")
    {
	if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling wait event\n", self_gid);
    }

    else if (event_type == "terminate")
    {
        //if(self_cid == 0) std::cout<<(getCurrentSimTimeNano()*0.000000001)<<"\n";
        if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Handling terminate event. Component simulation terminating\n", self_gid);
        
        primaryComponentOKToEndSim();
    }

}


void beComponent::finish()
{
    /*int i, j, k, l, call_i = 0, comm_i = 0, event_number = 0;
    std::ofstream trace_op;
    trace_op.open("event_trace.txt", std::ios::out | std::ios::app);

    for(i = 0; i < call_records.size()+comm_records.size(); i++)
    {

        if(call_i < call_records.size())
        {

            if((std::get<2>(call_records[call_i])[1]) == event_number+1)
            {   
                trace_op<<"("<<std::get<0>(call_records[call_i])<<", '"<<std::get<1>(call_records[call_i])<<"', ["<<(std::get<2>(call_records[call_i])[0])<<", "<<(std::get<2>(call_records[call_i])[1])<<"], '"<<std::get<3>(call_records[call_i])<<"', ["<<(std::get<4>(call_records[call_i])[0])<<", "<<(std::get<4>(call_records[call_i])[1])<<"], '"<<std::get<5>(call_records[call_i])<<"', [";

                std::vector<int> parameters = std::get<6>(call_records[call_i]);

	        for(j = 0; j < parameters.size(); j++){
                    trace_op<<parameters[j];
                    if(j+1 < parameters.size()) trace_op<<", ";
                }

                trace_op<<"])\n";

                call_i++;
                event_number++;
            }
    
        }

        if(comm_i < comm_records.size())
        {

            if(self_gid != std::get<0>(comm_records[comm_i]))
            {

                trace_op<<"("<<std::get<0>(comm_records[comm_i])<<", '"<<std::get<1>(comm_records[comm_i])<<"', ("<<std::get<0>(std::get<2>(comm_records[comm_i]))<<", "<<std::get<2>(std::get<2>(comm_records[comm_i]))<<"), "<<"("<<std::get<0>(std::get<3>(comm_records[comm_i]))<<", "<<std::get<1>(std::get<3>(comm_records[comm_i]))<<"), "<<"[";

                std::vector< std::tuple<int, std::tuple<double, double>, std::string, std::vector<int>, std::vector<int>> > messagePath = std::get<4>(comm_records[comm_i]);

                for(k = 0; k < messagePath.size(); k++)
                {
                    trace_op<<"("<<std::get<0>(messagePath[k])<<", ("<<std::get<0>(std::get<1>(messagePath[k]))<<", "<<std::get<1>(std::get<1>(messagePath[k]))<<"), '"<<std::get<2>(messagePath[k])<<"', [";
                    std::vector<int> mparameters = std::get<3>(messagePath[k]);

	            for(j = 0; j < mparameters.size(); j++){
                        trace_op<<mparameters[j];
                        if(j+1 < mparameters.size()) trace_op<<", ";
                    }

                    std::vector<int> mlocations = std::get<4>(messagePath[k]);
                    trace_op<<"], [";

                    for(l = 0; l < mlocations.size(); l++){
                        trace_op<<mlocations[l];
                        if(l+1 < mlocations.size()) trace_op<<", ";
                    }

                    if(k+1 < messagePath.size()) trace_op<<"]), ";
                }   

                trace_op<<"])])\n";

                comm_i++;
            }   

            else if(std::get<2>(std::get<2>(comm_records[comm_i])) == event_number+1)
            {
                trace_op<<"("<<std::get<0>(comm_records[comm_i])<<", '"<<std::get<1>(comm_records[comm_i])<<"', ("<<std::get<0>(std::get<2>(comm_records[comm_i]))<<", "<<std::get<2>(std::get<2>(comm_records[comm_i]))<<"), "<<"("<<std::get<0>(std::get<3>(comm_records[comm_i]))<<", "<<std::get<1>(std::get<3>(comm_records[comm_i]))<<"), "<<"[";

                std::vector< std::tuple<int, std::tuple<double, double>, std::string, std::vector<int>, std::vector<int>> > messagePath = std::get<4>(comm_records[comm_i]);

                for(k = 0; k < messagePath.size(); k++)
                {
                    trace_op<<"("<<std::get<0>(messagePath[k])<<", ("<<std::get<0>(std::get<1>(messagePath[k]))<<", "<<std::get<1>(std::get<1>(messagePath[k]))<<"), '"<<std::get<2>(messagePath[k])<<"', [";
                    std::vector<int> mparameters = std::get<3>(messagePath[k]);

	            for(j = 0; j < mparameters.size(); j++){
                        trace_op<<mparameters[j];
                        if(j+1 < mparameters.size()) trace_op<<", ";
                    }

                    std::vector<int> mlocations = std::get<4>(messagePath[k]);
                    trace_op<<"], [";

                    for(l = 0; l < mlocations.size(); l++){
                        trace_op<<mlocations[l];
                        if(l+1 < mlocations.size()) trace_op<<", ";
                    }

                    if(k+1 < messagePath.size()) trace_op<<"]), ";
                }   

                trace_op<<"])])\n";

                comm_i++;
                event_number++;
            }
        }

    }

    trace_op.close();
   */ 
        
    Py_Finalize();

    //if((simulation_handler->sim_flags)->debug == self_gid) printf("GID: %d -- Component exiting!\n", self_gid);
   
}

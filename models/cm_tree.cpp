/*
 *  cm_tree.cpp
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
#include "cm_tree.h"


// compartment compartment functions ///////////////////////////////////////////
nest::Compartment::Compartment( const long compartment_index,
                                const long parent_index )
  : xx_( 0.0 )
  , yy_( 0.0 )
  , comp_index( compartment_index )
  , p_index( parent_index )
  , parent( nullptr )
  , v_comp( 0.0 )
  , ca( 1.0)
  , gc( 0.01)
  , gl( 0.1 )
  , el( -70.)
  , ff( 0.0 )
  , gg( 0.0 )
  , hh( 0.0 )
  , n_passed( 0 )
{
  compartment_currents = CompartmentCurrents();
};
nest::Compartment::Compartment( const long compartment_index,
                                const long parent_index,
			                          const DictionaryDatum& compartment_params )
  : xx_( 0.0 )
  , yy_( 0.0 )
  , comp_index( compartment_index )
  , p_index( parent_index )
  , parent( nullptr )
  , v_comp( getValue< double >( compartment_params, "e_L" ) )
  , ca( getValue< double >( compartment_params, "C_m" ) )
  , gc( getValue< double >( compartment_params, "g_c" ) )
  , gl( getValue< double >( compartment_params, "g_L" ) )
  , el( getValue< double >( compartment_params, "e_L" ) )
  , ff( 0.0 )
  , gg( 0.0 )
  , hh( 0.0 )
  , n_passed( 0 )
{
  compartment_currents = CompartmentCurrents(compartment_params);
};

void
nest::Compartment::init()
{
    v_comp = el;
    compartment_currents.init();

    // initialize the buffer
    currents.clear();
}

std::map< std::string, double* >
nest::Compartment::get_recordables()
{
    std::map< std::string, double* > recordables =
        compartment_currents.get_recordables(comp_index);

    recordables.insert(recordables.begin(), recordables.end());
    recordables["v_comp" + std::to_string(comp_index)] = &v_comp;

    return recordables;
}

// for matrix construction
void
nest::Compartment::construct_matrix_element( const long lag )
{
    const double dt = Time::get_resolution().get_ms();

    // matrix diagonal element
    gg = ca / dt + gl / 2.;

    if( parent != nullptr )
    {
        gg += gc / 2.;
        // matrix off diagonal element
        hh = -gc / 2.;
    }

    for( auto child_it = children.begin();
         child_it != children.end();
         ++child_it )
    {
        gg += (*child_it).gc / 2.;
    }

    // right hand side
    ff = ca / dt * v_comp - gl * (v_comp / 2. - el);

    if( parent != nullptr )
    {
        ff -= gc * (v_comp - parent->v_comp) / 2.;
    }

    for( auto child_it = children.begin();
         child_it != children.end();
         ++child_it )
    {
        ff -= (*child_it).gc * (v_comp - (*child_it).v_comp) / 2.;
    }

    // add all currents to compartment
    std::pair< double, double > gi = compartment_currents.f_numstep( v_comp, dt, lag );
    gg += gi.first;
    ff += gi.second;

    // add input current
    ff += currents.get_value( lag );
}
////////////////////////////////////////////////////////////////////////////////


// compartment tree functions //////////////////////////////////////////////////
nest::CompTree::CompTree()
  : root_( 0, -1)
{
  compartments_.resize( 0 );
  leafs_.resize( 0 );
}

/*
Add a compartment to the tree structure via the python interface
root shoud have -1 as parent index. Add root compartment first.
Assumes parent of compartment is already added
*/
void
nest::CompTree::add_compartment( const long compartment_index,
                                 const long parent_index,
			                           const DictionaryDatum& compartment_params )
{
    Compartment* compartment = new Compartment( compartment_index, parent_index,
                				                        compartment_params );

    if( parent_index >= 0 )
    {
        Compartment* parent = get_compartment( parent_index );
        parent->children.push_back( *compartment );
    }
    else
    {
        root_ = *compartment;
    }

    compartment_indices_.push_back(compartment_index);

    set_compartments();
};

/*
Get the compartment corresponding to the provided index in the tree.

This function gets the compartments by a recursive search through the tree.

The overloaded functions looks only in the subtree of the provided compartment,
and also has the option to throw an error if no compartment corresponding to
`compartment_index` is found in the tree
*/
nest::Compartment*
nest::CompTree::get_compartment( const long compartment_index )
{
    return get_compartment( compartment_index, get_root(), 1 );
}
nest::Compartment*
nest::CompTree::get_compartment( const long compartment_index,
                                 Compartment* compartment,
                                 const long raise_flag )
{
    Compartment* r_compartment = nullptr;

    if( compartment->comp_index == compartment_index )
    {
        r_compartment = compartment;
    }
    else
    {
        auto child_it = compartment->children.begin();
        while( !r_compartment && child_it != compartment->children.end() )
        {
            r_compartment = get_compartment( compartment_index, &(*child_it), 0 );
            ++child_it;
        }
    }

    if( !r_compartment && raise_flag )
    {
        std::ostringstream err_msg;
        err_msg << "Node index " << compartment_index << " not in tree";
        throw BadProperty(err_msg.str());
    }

    return r_compartment;
}

/*
Initialize all tree structure pointers
*/
void
nest::CompTree::init_pointers()
{
  set_parents();
  set_compartments();
  set_leafs();
}
/*
For each compartments, sets its pointer towards its parent compartment
*/
void
nest::CompTree::set_parents()
{
  for( auto compartment_idx_it = compartment_indices_.begin();
       compartment_idx_it != compartment_indices_.end();
       ++compartment_idx_it )
  {
    Compartment* comp_ptr   = get_compartment( *compartment_idx_it );
    // will be nullptr if root
    Compartment* parent_ptr = get_compartment( comp_ptr->p_index,
                                               &root_, 0 );
    comp_ptr->parent = parent_ptr;
  }
}
/*
Creates a vector of compartment pointers, organized in the order in which they were
added by `add_compartment()`
*/
void
nest::CompTree::set_compartments()
{
    compartments_.clear();

    for( auto compartment_idx_it = compartment_indices_.begin();
         compartment_idx_it != compartment_indices_.end();
         ++compartment_idx_it )
    {
        compartments_.push_back( get_compartment( *compartment_idx_it ) );
    }

}
/*
Creates a vector of compartment pointers of compartments that are also leafs of the tree.
*/
void
nest::CompTree::set_leafs()
{
    leafs_.clear();
    for( auto compartment_it = compartments_.begin();
         compartment_it != compartments_.end();
         ++compartment_it )
    {
        if( int((*compartment_it)->children.size()) == 0 )
  {
            leafs_.push_back( *compartment_it );
        }
    }
};

/*
Returns a map of variable names and pointers to the recordables
*/
std::map< std::string, double* >
nest::CompTree::get_recordables()
{
  std::map< std::string, double* > recordables;

  /*
  add recordables for all compartments, suffixed by compartment_idx,
  to "recordables"
  */
  for( auto compartment_it = compartments_.begin();
     compartment_it != compartments_.end();
     ++compartment_it )
  {
    std::map< std::string, double* > recordables_comp =
                                          ( *compartment_it )->get_recordables();
    recordables.insert(recordables_comp.begin(), recordables_comp.end());
  }
  return recordables;
}

/*
Initialize state variables
*/
void
nest::CompTree::init()
{
  // initialize the compartments
  for( auto compartment_it = compartments_.begin();
       compartment_it != compartments_.end();
       ++compartment_it )
  {
    ( *compartment_it )->init();
  }
}

/*
Returns vector of voltage values, indices correspond to compartments in `compartments_`
*/
std::vector< double >
nest::CompTree::get_voltage() const
{
    std::vector< double > v_comps;
    for( auto compartment_it = compartments_.cbegin();
         compartment_it != compartments_.cend();
         ++compartment_it )
    {
        v_comps.push_back( (*compartment_it)->v_comp );
    }
    return v_comps;
}

/*
Return voltage of single compartment voltage, indicated by the compartment_index
*/
double
nest::CompTree::get_compartment_voltage( const long compartment_index )
{
    const Compartment* compartment = get_compartment( compartment_index );
    return compartment->v_comp;
}

/*
Construct the matrix equation to be solved to advance the model one timestep
*/
void
nest::CompTree::construct_matrix( const long lag )
{
    for( auto compartment_it = compartments_.begin();
         compartment_it != compartments_.end();
         ++compartment_it )
    {
        (*compartment_it)->construct_matrix_element( lag );
    }
};

/*
Solve matrix with O(n) algorithm
*/
void
nest::CompTree::solve_matrix()
{
    std::vector< Compartment* >::iterator leaf_it = leafs_.begin();

    // start the down sweep (puts to zero the sub diagonal matrix elements)
    solve_matrix_downsweep(leafs_[0], leaf_it);

    // do up sweep to set voltages
    solve_matrix_upsweep(&root_, 0.0);
};
void
nest::CompTree::solve_matrix_downsweep( Compartment* compartment,
					     std::vector< Compartment* >::iterator leaf_it )
{
    // compute the input output transformation at compartment
    std::pair< double, double > output = compartment->io();

    // move on to the parent layer
    if( compartment->parent != nullptr )
    {
        Compartment* parent = compartment->parent;
        // gather input from child layers
        parent->gather_input(output);
        // move on to next compartments
        ++parent->n_passed;
        if(parent->n_passed == int(parent->children.size()))
	{
            parent->n_passed = 0;
            // move on to next compartment
            solve_matrix_downsweep(parent, leaf_it);
        }
	else
	{
            // start at next leaf
            ++leaf_it;
            if(leaf_it != leafs_.end())
	    {
	      solve_matrix_downsweep(*leaf_it, leaf_it);
	    }
        }
    }
};
void
nest::CompTree::solve_matrix_upsweep( Compartment* compartment, double vv )
{
    // compute compartment voltage
    vv = compartment->calc_v(vv);
    // move on to child compartments
    for( auto child_it = compartment->children.begin();
         child_it != compartment->children.end();
         ++child_it )
    {
        solve_matrix_upsweep(&(*child_it), vv);
    }
};

/*
Print the tree graph
*/
void
nest::CompTree::print_tree() const
{
    // loop over all compartments
    std::printf(">>> CM tree with %d compartments <<<\n", int(compartments_.size()));
    for(int ii=0; ii<int(compartments_.size()); ++ii)
    {
        Compartment* compartment = compartments_[ii];
        std::cout << "    Compartment " << compartment->comp_index << ": ";
        std::cout << "C_m = " << compartment->ca << " nF, ";
        std::cout << "g_L = " << compartment->gl << " uS, ";
        std::cout << "e_L = " << compartment->el << " mV, ";
        if(compartment->parent != nullptr)
        {
            std::cout << "Parent " << compartment->parent->comp_index << " --> ";
            std::cout << "g_c = " << compartment->gc << " uS, ";
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
};
////////////////////////////////////////////////////////////////////////////////

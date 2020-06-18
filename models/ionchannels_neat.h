#include <iostream>
#include <string>
#include <vector>
#include <list>
#include <map>
#include <complex>
#include <tuple>
#include <numeric>
#include <cmath>
#include <string.h>
#include <stdlib.h>
#include <algorithm>
#include <math.h>
#include <time.h>

#include "nest_time.h"

namespace nest{


class IonChannel{
public:
    virtual void init(){};

    virtual void reset(){};
    virtual void update(){};
    virtual void add_spike(){};
    virtual std::pair< double, double > f_numstep( const double v_comp ){ return std::make_pair( 0., 0. ); };
};


class FakeChannel: public IonChannel{
protected:
    // step for AP
    double m_g_step = 0.0;
    // reversal of ion channel
    double m_e_r = 0.;
    // conductance g
    double m_g_r = 0.0, m_g_d = 0.0;
    double m_g = 0.0;
    // time scales window
    double m_tau_r = .2, m_tau_d = 3.;
    double m_norm;
    // propagators
    double m_p_r = 0.0, m_p_d = 0.0;

public:
    FakeChannel(){set_params(.1, 1., 0., 1.);};
    FakeChannel(double tau_r, double tau_d, double e_r, double g_step);

    void init() override;
    void set_params(double tau_r, double tau_d, double e_r, double g_step);

    void reset() override {m_g = 0.0;};
    void add_spike() override;
    void update() override;
    std::pair< double, double > f_numstep(const double v_comp) override;
};


class FakePotassium: public FakeChannel{
public:
    FakePotassium(double g_step){set_params(.3, 4., -85., g_step);};
};
class FakeSodium: public FakeChannel{
public:
    FakeSodium(double g_step){set_params(.1, .5, 50., g_step);};
};

} // namespace